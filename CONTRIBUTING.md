# Contributing to DataOps Foundation

🎉 ขอบคุณที่สนใจช่วยพัฒนา DataOps Foundation! 

## 🚀 การเริ่มต้น

### ข้อกำหนดเบื้องต้น

- Python 3.9+
- Git
- Docker (ไม่บังคับ)

### การตั้งค่า Development Environment

1. **Fork และ Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dataops-foundation.git
   cd dataops-foundation
   ```

2. **ตั้งค่า Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # หรือ
   venv\Scripts\activate     # Windows
   ```

3. **ติดตั้ง Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # ติดตั้งแบบ editable mode
   ```

4. **รันการทดสอบ**
   ```bash
   python tests/test_enhanced_etl.py
   pytest tests/ -v
   ```

## 📋 การมีส่วนร่วม

### 🐛 การรายงาน Bug

หากพบ bug กรุณาสร้าง issue ใหม่พร้อมข้อมูล:
- รายละเอียดของปัญหา
- ขั้นตอนการทำซ้ำ
- Environment information
- Error messages หรือ logs

### 💡 การเสนอ Feature ใหม่

สำหรับ feature ใหม่:
1. สร้าง issue เพื่อหารือก่อน
2. อธิบายปัญหาที่ feature นี้จะแก้ไข
3. เสนอวิธีการ implementation

### 🔧 การส่ง Pull Request

1. **สร้าง Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **พัฒนาและทดสอบ**
   ```bash
   # เขียนโค้ด
   # เพิ่ม tests
   # รัน tests
   pytest tests/ -v
   ```

3. **ตรวจสอบ Code Quality**
   ```bash
   # Code formatting
   black src/ tests/
   
   # Linting
   flake8 src/ tests/
   
   # Security check
   bandit -r src/
   ```

4. **Commit และ Push**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

5. **สร้าง Pull Request**
   - ไปที่ GitHub และสร้าง PR
   - อธิบายการเปลี่ยนแปลง
   - เชื่อมโยงกับ issue ที่เกี่ยวข้อง

## 📝 Code Style Guidelines

### Python Code Style

- ใช้ **Black** สำหรับ code formatting
- ใช้ **flake8** สำหรับ linting
- ใช้ **Type hints** ทุกครั้งที่เป็นไปได้
- ตั้งชื่อ variables และ functions ให้ชัดเจน

### Documentation

- เขียน docstrings สำหรับ classes และ functions
- อัปเดต README.md หากมีการเปลี่ยนแปลง API
- เพิ่ม type hints และ comments ที่จำเป็น

### Testing

- เขียน unit tests สำหรับ functions ใหม่
- เขียน integration tests สำหรับ features ใหม่
- รักษา test coverage ไว้ที่ 80%+

## 🧪 การทดสอบ

### รันการทดสอบทั้งหมด

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Enhanced ETL tests
python tests/test_enhanced_etl.py

# Performance tests
pytest tests/performance/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=src --cov-report=html
# เปิด htmlcov/index.html
```

## 📦 การ Release

### Semantic Versioning

เราใช้ [Semantic Versioning](https://semver.org/):
- **MAJOR**: การเปลี่ยนแปลงที่ไม่ backward compatible
- **MINOR**: การเพิ่ม functionality ที่ backward compatible
- **PATCH**: การแก้ไข bug ที่ backward compatible

### Release Process

1. อัปเดต version ใน `src/__init__.py`
2. อัปเดต CHANGELOG.md
3. สร้าง Git tag
4. สร้าง GitHub release

## 🏗️ โครงสร้างโปรเจค

```
dataops-foundation/
├── src/                    # โค้ดหลัก
│   ├── data_pipeline/      # ETL processing
│   ├── data_quality/       # Data quality checks
│   ├── monitoring/         # Metrics & monitoring
│   └── utils/              # Utilities
├── tests/                  # Tests
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── performance/       # Performance tests
├── config/                # Configuration files
├── docker/                # Docker configs
├── docs/                  # Documentation
└── examples/              # Examples & sample data
```

## 💬 การสื่อสาร

- **GitHub Issues**: สำหรับ bugs และ feature requests
- **GitHub Discussions**: สำหรับคำถามและการหารือ
- **Email**: dataops@company.com

## 🙏 การขอบคุณ

- รายชื่อ contributors จะถูกเพิ่มใน README.md
- การมีส่วนร่วมทุกรูปแบบมีค่า ไม่ว่าจะเป็น code, documentation, หรือ feedback

## 📄 License

โปรเจคนี้ใช้ MIT License - ดูรายละเอียดใน [LICENSE](LICENSE)

---

**Happy Contributing! 🎉**
