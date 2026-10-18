#!/usr/bin/env python3
"""Measure CPU ONNX Runtime peak RSS and latency for the exported model."""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import psutil

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=ROOT / "outputs/onnx")
    parser.add_argument("--count", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/onnx/memory-benchmark.json")
    args = parser.parse_args()

    model_dir = args.model_dir if args.model_dir.is_absolute() else ROOT / args.model_dir
    model_path, meta_path = model_dir / "image-anime-generator.onnx", model_dir / "metadata.json"
    if not model_path.is_file() or not meta_path.is_file():
        parser.error("Model not found. Train and export IMAGE's own model before benchmarking.")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(model_path), sess_options=options, providers=["CPUExecutionProvider"])
    vocab = metadata["vocab"]
    sizes = [len(vocab[name]) for name in metadata["attributes"]]
    rng = np.random.default_rng(args.seed)
    process = psutil.Process(os.getpid())
    peak_rss = [process.memory_info().rss]
    stop = threading.Event()

    def monitor() -> None:
        while not stop.is_set():
            try:
                peak_rss[0] = max(peak_rss[0], process.memory_info().rss)
            except psutil.Error:
                pass
            stop.wait(0.01)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    started = time.perf_counter()
    generated = 0
    try:
        while generated < args.count:
            batch = min(max(1, args.batch_size), args.count - generated)
            noise = rng.standard_normal((batch, int(metadata["latent_dim"])), dtype=np.float32)
            labels = np.stack([
                rng.integers(0, size, size=batch, dtype=np.int64) for size in sizes
            ], axis=1)
            session.run(["rgba"], {"noise": noise, "labels": labels})
            generated += batch
    finally:
        stop.set()
        monitor_thread.join(timeout=1)
    elapsed = time.perf_counter() - started
    peak_rss[0] = max(peak_rss[0], process.memory_info().rss)
    result = {
        "model_origin": metadata.get("model_origin"),
        "pretrained_checkpoint_used": metadata.get("pretrained_checkpoint_used"),
        "model_file": model_path.name,
        "count": generated,
        "batch_size": args.batch_size,
        "elapsed_seconds": round(elapsed, 4),
        "milliseconds_per_image": round(elapsed * 1000 / max(1, generated), 3),
        "peak_rss_mib": round(peak_rss[0] / (1024 * 1024), 2),
        "system_ram_target_mib": 2048,
        "within_2gb_process_peak": peak_rss[0] <= 2048 * 1024 * 1024,
        "measurement_note": "Peak RSS is measured for this process, not total OS memory; repeat on the target PC with the editor running for final acceptance."
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
