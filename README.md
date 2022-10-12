# GatewayRAMDumPYer
Tools to handle files dumped by CTRPF's GatewayRAMDumper from Python

# Example
```python
Process = GatewayRAMDumper("./DUMP.bin")
print(hex(Process.read32(0x100000)))
```
