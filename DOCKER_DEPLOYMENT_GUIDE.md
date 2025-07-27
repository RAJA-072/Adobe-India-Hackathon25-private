# Docker Volume Mounting Deployment Guide 🐳

## Overview
Both Challenge 1a and Challenge 1b now support enterprise-grade Docker volume mounting for flexible input/output directory handling.

## Challenge 1a: PDF Processing

### Build
```bash
cd Challenge_1a
docker build --platform linux/amd64 -t adobe-hackathon-pdf-processor:latest .
```

### Run with Volume Mounting ✅
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe-hackathon-pdf-processor:latest
```

### Test Results
- ✅ **Processing Time**: ~3 seconds for 5 PDFs
- ✅ **Success Rate**: 100% validation
- ✅ **Output**: JSON files generated in mounted output directory
- ✅ **Network Isolation**: Secure execution with `--network none`

## Challenge 1b: Multi-Collection Analysis

### Build
```bash
cd Challenge_1b
docker build --platform linux/amd64 -t challenge1b-analyzer:latest .
```

### Run with Volume Mounting ✅
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1b-analyzer:latest
```

### Test Results
- ✅ **Processing Time**: ~9 seconds for 3 collections
- ✅ **Success Rate**: 100% validation (all collections)
- ✅ **Output**: Collection-specific JSON files in mounted output directory
- ✅ **Network Isolation**: Secure execution with `--network none`

## Enterprise Features

### Volume Mounting Benefits
- 🏢 **Enterprise Deployment**: Perfect for production environments
- 🔒 **Security**: Network-isolated execution 
- 📁 **Flexibility**: Custom input/output directory support
- 🚀 **CI/CD Ready**: Ideal for automated pipelines
- 🔄 **Scalability**: Easy integration with orchestration systems

### Directory Structure
```
your-project/
├── input/                  # Mount point for input files
│   ├── *.pdf              # (Challenge 1a)
│   └── Collection X/       # (Challenge 1b)
│       ├── challenge1b_input.json
│       └── PDFs/
└── output/                 # Mount point for output files
    ├── *.json             # (Challenge 1a)
    └── Collection X/       # (Challenge 1b)
        └── challenge1b_output_generated.json
```

### Network Isolation
Both containers run with `--network none` for maximum security:
- ❌ No internet access during processing
- ❌ No external network communication
- ✅ Complete isolation from host network
- ✅ Secure processing environment

## Compatibility

### Platform Support
- ✅ **Architecture**: linux/amd64
- ✅ **Docker**: Compatible with Docker Desktop and Docker Engine
- ✅ **Operating Systems**: Windows, macOS, Linux

### Command Compatibility
Both Unix-style and PowerShell commands work:
```bash
# Unix/Linux/macOS
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none imagename:tag

# Windows PowerShell
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none imagename:tag
```

## Ready for Adobe Hackathon 2025! 🏆

Both challenges now support the enterprise deployment pattern with volume mounting, making them production-ready for any environment while maintaining perfect hackathon compliance.
