## What was run, and what failed

Commands (from `agent/`, with `.venv-d1`, pinned in `decision/requirements-d1.txt`; python 3.12.10, torch 2.14.1+cu130, transformers 5.19.0; models `LiquidAI/d1-omni-600M` and `LiquidAI/d1-3B`, remote code revisions as downloaded on 2026-10-09; GPU RTX 3060 12 GB, about 2 GB used by the desktop before the runs):

```
python decision/zero_shot_d1.py --model d1-omni-600M --split heldout --limit 20                       # smoke, cuda, float16
python decision/zero_shot_d1.py --model d1-omni-600M --split heldout                                  # 720 rows
python decision/zero_shot_d1.py --model d1-omni-600M --split bench                                    # 900 rows
python decision/zero_shot_d1.py --model d1-3B --split heldout --limit 20                              # smoke on cuda: FAILED, see below
python decision/zero_shot_d1.py --model d1-3B --split heldout --limit 10 --device cpu --warmup 1      # smoke, cpu
python decision/zero_shot_d1.py --model d1-3B --split heldout --limit 120 --stride 6 --device cpu --warmup 1
python decision/zero_shot_d1.py --model d1-3B --split bench --limit 112 --stride 8 --device cpu --warmup 1
python decision/zero_shot_d1.py --model d1-omni-600M --split heldout --limit 120 --stride 6           # same rows as the 3B run
python decision/zero_shot_d1.py --model d1-omni-600M --split bench --limit 112 --stride 8
```

`--stride K` (every K-th row) is an addition to the requested flags: the jsonl files are ordered by exercise, so the first N rows would cover only 3 or 4 exercises; a stride spreads the CPU runs over all 20 (held-out) or 25 (bench) exercises. The 600M was re-run on the same strided rows so that the two models can be compared on identical rows.

**d1-3B does not run on the GPU here.** The weights load on cuda in bfloat16 (nvidia-smi: 6761 MiB used of 12288 after load, torch allocated 5969 MiB; they fit), and the first `system_one` call fails in the model's own remote code (`hybrid.py`, `_own`, line 174, the fused path taken for a CUDA half-precision tensor on compute capability 8.x):

```
torch.ops.aten._flash_attention_forward(...)
RuntimeError: USE_FLASH_ATTENTION was not enabled for build.
```

The RTX 3060 (compute capability 8.6) has the hardware for it; what is missing is the flash-attention kernel in the PyTorch Windows wheel (`torch 2.14.1+cu130`, `torch.backends.cuda.flash_sdp_enabled()` is True but the op is not compiled in). The code has a non-fused path (`_explicit`) but it is only chosen on CPU or in float32, so no workaround was tried on the GPU (no patch of the remote code, no float32 on cuda): the failure is documented and the 3B was run on CPU, in float32, as the model card does on CPU. Next options, not done: Linux or WSL with a PyTorch build that includes flash attention (the same environment step 3 needs for Unsloth), or a PyTorch build for Windows with `USE_FLASH_ATTENTION`.

**Consequences for the numbers.** The 3B figures are on 120 held-out rows and 112 bench rows (a subset, about 14.2 s per row on 12 CPU threads, 28 and 26 minutes), not on the full sets; the 3B and 600M times are on different devices and are not a speed comparison. The 600M on the same subsets is in the table above.
