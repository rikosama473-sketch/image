/* 
 * IMAGE advanced local editing operations.
 * Adapted from the user's own AnimeArt repository:
 * https://github.com/jonhararagi/animeart/tree/main/web/domain
 * Background removal: background-removal.mjs
 * Color replacement: color-replacement.mjs
 * Layer adjustments: layer-adjustments.mjs
 * No model downloads, network inference, or source-file writes.
 */
(() => {
  "use strict";
  const background = (() => {
    const MAX_PIXELS=16_000_000;
    function parseColor(color){if(Array.isArray(color)&&color.length>=3)return color.slice(0,3).map(v=>Math.max(0,Math.min(255,Number(v)||0)));const m=/^#?([0-9a-f]{6})$/i.exec(String(color||""));if(!m)throw new TypeError("Background color must be a six-digit RGB hex value");return[0,2,4].map(i=>parseInt(m[1].slice(i,i+2),16));}
    function validate(image,operation){const width=Number(image?.width),height=Number(image?.height),data=image?.data;if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width*height>MAX_PIXELS||!data||data.length!==width*height*4)throw new TypeError(operation+" requires valid image pixels up to 16 megapixels");return{width,height,data};}
    function distance(data,offset,target){const r=data[offset]-target[0],g=data[offset+1]-target[1],b=data[offset+2]-target[2];return Math.sqrt((r*r+g*g+b*b)/3);}
    function unmatte(data,offset,target,alpha){if(alpha<=0||alpha>=1)return;for(let c=0;c<3;c++)data[offset+c]=Math.max(0,Math.min(255,Math.round((data[offset+c]-target[c]*(1-alpha))/alpha)));}
    /**
     * Local, non-AI edge-connected matte for flat backgrounds. Strong local color
     * transitions stop flood propagation, protecting black ink and warm/cool fills.
     * Feathering is restricted to the connected fringe to avoid leaking through lines.
     */
    function removeConnectedBackground(imageData,{targetColor="#ffffff",tolerance=36,feather=18,edgeSensitivity=42,protectLineArt=true,decontaminate=true,seedPoints=[],mutate=false}={}){
     const{width,height,data:source}=validate(imageData,"Background removal"),target=parseColor(targetColor),threshold=Math.max(0,Math.min(255,Number(tolerance)||0)),soft=Math.max(0,Math.min(100,Number(feather)||0)),edge=Math.max(0,Math.min(180,Number(edgeSensitivity)||0)),reach=Math.min(255,threshold+soft),count=width*height,data=mutate?source:new Uint8ClampedArray(source),visited=new Uint8Array(count);let queue=new Int32Array(Math.min(count,Math.max(1024,width*2+height*2))),queueHead=0,queueTail=0,queueSize=0;
     const enqueue=index=>{if(queueSize===queue.length){if(queue.length>=count)throw new RangeError("Background-removal queue exceeded the pixel count");const nextCapacity=Math.min(count,queue.length*2),expanded=new Int32Array(nextCapacity);for(let offset=0;offset<queueSize;offset++)expanded[offset]=queue[(queueHead+offset)%queue.length];queue=expanded;queueHead=0;queueTail=queueSize;}queue[queueTail]=index;queueTail++;if(queueTail===queue.length)queueTail=0;queueSize++;};
     const d=i=>distance(data,i*4,target);
     function seed(i){if(visited[i])return;const o=i*4;if(data[o+3]===0||d(i)>threshold)return;visited[i]=1;enqueue(i);}
     const explicitSeeds=Array.isArray(seedPoints)?seedPoints.filter(p=>p&&Number.isFinite(Number(p.x))&&Number.isFinite(Number(p.y))):[];
     if(explicitSeeds.length){for(const p of explicitSeeds){const x=Math.max(0,Math.min(width-1,Math.floor(Number(p.x)))),y=Math.max(0,Math.min(height-1,Math.floor(Number(p.y))));seed(y*width+x);}}
     else {for(let x=0;x<width;x++){seed(x);if(height>1)seed((height-1)*width+x);}
     for(let y=1;y<height-1;y++){seed(y*width);if(width>1)seed(y*width+width-1);}}
     const visitNeighbor=(n,currentOffset)=>{if(visited[n])return;const o=n*4;if(data[o+3]===0){visited[n]=1;return;}const nd=d(n);if(nd>reach)return;
      if(protectLineArt){const delta=Math.sqrt(((data[o]-data[currentOffset])**2+(data[o+1]-data[currentOffset+1])**2+(data[o+2]-data[currentOffset+2])**2)/3);if(delta>edge)return;}
      visited[n]=1;if(nd<=threshold)enqueue(n);};
     while(queueSize>0){const i=queue[queueHead];queueHead++;if(queueHead===queue.length)queueHead=0;queueSize--;const x=i%width,y=Math.floor(i/width),currentOffset=i*4;if(x)visitNeighbor(i-1,currentOffset);if(x+1<width)visitNeighbor(i+1,currentOffset);if(y)visitNeighbor(i-width,currentOffset);if(y+1<height)visitNeighbor(i+width,currentOffset);}
     let changed=false;for(let i=0;i<count;i++){if(!visited[i])continue;const o=i*4,dist=d(i),beforeAlpha=data[o+3];if(dist<=threshold)data[o+3]=0;else if(soft>0){const a=Math.max(0,Math.min(1,(dist-threshold)/soft));data[o+3]=Math.round(data[o+3]*a);if(decontaminate)unmatte(data,o,target,a);}if(data[o+3]!==beforeAlpha)changed=true;}
     return{width,height,data,changed};
    }
    function applyEraseStrokes(imageData,strokes=[],{mutate=false}={}){const{width,height,data:source}=validate(imageData,"Manual erase"),data=mutate?source:new Uint8ClampedArray(source);for(const stroke of Array.isArray(strokes)?strokes:[]){const size=Number(stroke?.size),points=Array.isArray(stroke?.points)?stroke.points:[];if(!Number.isFinite(size)||size<=0||!points.length)continue;const radius=size/2,erase=p=>{const minX=Math.max(0,Math.floor(p.x-radius)),maxX=Math.min(width-1,Math.ceil(p.x+radius)),minY=Math.max(0,Math.floor(p.y-radius)),maxY=Math.min(height-1,Math.ceil(p.y+radius));for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++){const dx=x+.5-p.x,dy=y+.5-p.y;if(dx*dx+dy*dy<=radius*radius)data[(y*width+x)*4+3]=0;}};if(points.length===1){erase(points[0]);continue;}for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],distance=Math.hypot(b.x-a.x,b.y-a.y),steps=Math.max(1,Math.ceil(distance/Math.max(1,radius*.5)));for(let s=0;s<=steps;s++){const t=s/steps;erase({x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t});}}}return{width,height,data};}
    
    return { removeConnectedBackground, applyEraseStrokes };
  })();
  const color = (() => {
    const MAX_PIXELS=16_000_000;
    function parseColor(value){const m=/^#?([0-9a-f]{6})$/i.exec(String(value??""));if(!m)throw new TypeError("Colors must use six-digit RGB hex values");return[0,2,4].map(i=>parseInt(m[1].slice(i,i+2),16));}
    function rgbToHsl(r,g,b,out){r/=255;g/=255;b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min,l=(max+min)/2;let h=0,s=0;if(d){s=d/(1-Math.abs(2*l-1));if(max===r)h=((g-b)/d)%6;else if(max===g)h=(b-r)/d+2;else h=(r-g)/d+4;h*=60;if(h<0)h+=360;}out[0]=h;out[1]=s;out[2]=l;return out;}
    function hslToRgb(h,s,l,out){const c=(1-Math.abs(2*l-1))*s,x=c*(1-Math.abs((h/60)%2-1)),m=l-c/2;let r,g,b;if(h<60){r=c;g=x;b=0;}else if(h<120){r=x;g=c;b=0;}else if(h<180){r=0;g=c;b=x;}else if(h<240){r=0;g=x;b=c;}else if(h<300){r=x;g=0;b=c;}else{r=c;g=0;b=x;}out[0]=Math.max(0,Math.min(255,Math.round((r+m)*255)));out[1]=Math.max(0,Math.min(255,Math.round((g+m)*255)));out[2]=Math.max(0,Math.min(255,Math.round((b+m)*255)));return out;}
    function smooth(t){t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);}
    function replaceColorRange(imageData,{sourceColor="#806050",targetColor="#c76cf2",tolerance=36,softness=24,preserveShading=true,mutate=false}={}){const width=Number(imageData?.width),height=Number(imageData?.height),source=imageData?.data;if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width*height>MAX_PIXELS||!source||source.length!==width*height*4)throw new TypeError("Color replacement requires valid image pixels up to 16 megapixels");const from=parseColor(sourceColor),to=parseColor(targetColor),threshold=Math.max(0,Math.min(255,Number(tolerance)||0)),feather=Math.max(0,Math.min(160,Number(softness)||0)),targetHsl=rgbToHsl(to[0],to[1],to[2],[0,0,0]),data=mutate?source:new Uint8ClampedArray(source),pixelHsl=[0,0,0],replacement=[0,0,0];for(let i=0;i<data.length;i+=4){if(data[i+3]===0)continue;const red=data[i],green=data[i+1],blue=data[i+2],d=Math.sqrt(((red-from[0])**2+(green-from[1])**2+(blue-from[2])**2)/3);let weight;if(d<=threshold)weight=1;else if(feather>0&&d<threshold+feather)weight=1-smooth((d-threshold)/feather);else continue;rgbToHsl(red,green,blue,pixelHsl);const rgb=preserveShading?hslToRgb(targetHsl[0],targetHsl[1],pixelHsl[2],replacement):to;data[i]=Math.round(red*(1-weight)+rgb[0]*weight);data[i+1]=Math.round(green*(1-weight)+rgb[1]*weight);data[i+2]=Math.round(blue*(1-weight)+rgb[2]*weight);}return{width,height,data};}
    
    return { replaceColorRange };
  })();
  const adjustments = (() => {
    const DEFAULT_LAYER_ADJUSTMENTS = Object.freeze({
      brightness: 100,
      contrast: 100,
      saturation: 100,
      hue: 0,
      temperature: 0,
      tint: 0,
      blur: 0
    });
    
    const RULES = Object.freeze({
      brightness: { min: 0, max: 200, fallback: 100, precision: 1 },
      contrast: { min: 0, max: 200, fallback: 100, precision: 1 },
      saturation: { min: 0, max: 200, fallback: 100, precision: 1 },
      hue: { min: -180, max: 180, fallback: 0, precision: 1 },
      temperature: { min: -100, max: 100, fallback: 0, precision: 1 },
      tint: { min: -100, max: 100, fallback: 0, precision: 1 },
      blur: { min: 0, max: 20, fallback: 0, precision: 10 }
    });
    const KEYS = Object.freeze(Object.keys(RULES));
    
    function normalizeLayerAdjustments(value = {}) {
      const source = value && typeof value === "object" ? value : {};
      const normalized = {};
      for (const key of KEYS) {
        const rule = RULES[key];
        const raw = source[key];
        const numeric = raw === null || raw === "" || raw === undefined ? rule.fallback : Number(raw);
        const bounded = Number.isFinite(numeric)
          ? Math.min(rule.max, Math.max(rule.min, numeric))
          : rule.fallback;
        normalized[key] = Math.round(bounded * rule.precision) / rule.precision;
      }
      return normalized;
    }
    
    function isValidLayerAdjustments(value) {
      if (!value || typeof value !== "object" || Array.isArray(value)) return false;
      return KEYS.every(key => {
        const numeric = value[key];
        const rule = RULES[key];
        return typeof numeric === "number" &&
          Number.isFinite(numeric) &&
          numeric >= rule.min &&
          numeric <= rule.max;
      });
    }
    
    function areLayerAdjustmentsEqual(left, right) {
      const a = normalizeLayerAdjustments(left);
      const b = normalizeLayerAdjustments(right);
      return KEYS.every(key => a[key] === b[key]);
    }
    
    function isDefaultLayerAdjustments(value) {
      return areLayerAdjustmentsEqual(value, DEFAULT_LAYER_ADJUSTMENTS);
    }
    
    function layerAdjustmentsToCanvasFilter(value) {
      const adjustments = normalizeLayerAdjustments(value);
      const filters = [];
      if (adjustments.brightness !== 100) filters.push("brightness(" + adjustments.brightness + "%)");
      if (adjustments.contrast !== 100) filters.push("contrast(" + adjustments.contrast + "%)");
      if (adjustments.saturation !== 100) filters.push("saturate(" + adjustments.saturation + "%)");
      if (adjustments.hue !== 0) filters.push("hue-rotate(" + adjustments.hue + "deg)");
      if (adjustments.temperature > 0) {
        filters.push("sepia(" + Math.round(adjustments.temperature * 0.42) + "%)");
      } else if (adjustments.temperature < 0) {
        filters.push("hue-rotate(" + Math.round(adjustments.temperature * 0.12) + "deg)");
        filters.push("saturate(" + (100 + Math.round(Math.abs(adjustments.temperature) * 0.12)) + "%)");
      }
      if (adjustments.tint !== 0) {
        filters.push("hue-rotate(" + Math.round(adjustments.tint * 0.18) + "deg)");
        filters.push("saturate(" + (100 + Math.round(Math.abs(adjustments.tint) * 0.1)) + "%)");
      }
      if (adjustments.blur > 0) filters.push("blur(" + adjustments.blur + "px)");
      return filters.length ? filters.join(" ") : "none";
    }
    
    const LAYER_ADJUSTMENT_PRESETS = Object.freeze([
      Object.freeze({ id: "original", label: "Original", values: DEFAULT_LAYER_ADJUSTMENTS }),
      Object.freeze({ id: "anime", label: "Anime", values: Object.freeze({ brightness: 105, contrast: 114, saturation: 142, hue: 0, temperature: 0, tint: 0, blur: 0 }) }),
      Object.freeze({ id: "cinematic", label: "Cinematic", values: Object.freeze({ brightness: 92, contrast: 126, saturation: 112, hue: 8, temperature: -18, tint: 8, blur: 0 }) }),
      Object.freeze({ id: "manga", label: "Manga", values: Object.freeze({ brightness: 106, contrast: 152, saturation: 0, hue: 0, temperature: 0, tint: 0, blur: 0 }) }),
      Object.freeze({ id: "dream", label: "Dream", values: Object.freeze({ brightness: 108, contrast: 94, saturation: 118, hue: -12, temperature: 22, tint: -14, blur: 0.4 }) })
    ]);
    
    return {
      DEFAULT_LAYER_ADJUSTMENTS,
      normalizeLayerAdjustments,
      layerAdjustmentsToCanvasFilter,
      LAYER_ADJUSTMENT_PRESETS,
      isValidLayerAdjustments
    };
  })();
  window.ImageProEditing = Object.freeze({
    removeConnectedBackground: background.removeConnectedBackground,
    applyEraseStrokes: background.applyEraseStrokes,
    replaceColorRange: color.replaceColorRange,
    DEFAULT_LAYER_ADJUSTMENTS: adjustments.DEFAULT_LAYER_ADJUSTMENTS,
    normalizeLayerAdjustments: adjustments.normalizeLayerAdjustments,
    layerAdjustmentsToCanvasFilter: adjustments.layerAdjustmentsToCanvasFilter,
    LAYER_ADJUSTMENT_PRESETS: adjustments.LAYER_ADJUSTMENT_PRESETS,
    isValidLayerAdjustments: adjustments.isValidLayerAdjustments
  });
})();
