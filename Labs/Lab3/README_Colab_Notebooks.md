# LAB 3 Colab Notebooks - คู่มือการใช้งาน

## 📚 ภาพรวม

LAB 3 ประกอบด้วย 5 Notebooks สำหรับใช้งานบน Google Colab:

### Phase 1: I/Q Data Acquisition ✅
- **ไฟล์**: `Lab3_Phase1_IQ_Acquisition_Colab.ipynb`
- **เนื้อหา**: เชื่อมต่อ RTL-SDR ผ่าน rtl_tcp และ FRP
- **เวลา**: 45-60 นาที
- **สิ่งที่เรียนรู้**:
  - การใช้ rtl_tcp protocol
  - การรับ I/Q samples
  - การวิเคราะห์สเปกตรัม
  - Real-time monitoring

### Phase 2: ETI Stream Processing ✅
- **ไฟล์**: `Lab3_Phase2_ETI_Processing_Colab.ipynb`
- **เนื้อหา**: ทำความเข้าใจ ETI format และ parsing
- **เวลา**: 45-60 นาที
- **สิ่งที่เรียนรู้**:
  - ETI frame structure (6144 bytes)
  - การ parse header และ FIC
  - Sync status monitoring
  - Error rate tracking

## 🚀 การใช้งาน

### ข้อกำหนดเบื้องต้น:
1. Raspberry Pi 4 + RTL-SDR V4
2. FRP Client ทำงานบน RPI
3. rtl_tcp server รันที่ port 1234
4. Google Colab account


### การตั้งค่า FRP:
```bash
# บน RPI
rtl_tcp -a 0.0.0.0 -p 1234 -f 185.36e6 -s 2.048e6 -g 30
```

### ใน Colab:
1. อัพโหลด notebook
2. เปลี่ยน `FRP_SERVER` และ `FRP_PORT`
3. Run ทีละ cell
4. ทำตาม TODO comments

## 📖 เอกสารประกอบ:
- [LAB3.md](LAB3.md) - คู่มือฉบับเต็ม
- [FRP.md](../../FRP.md) - การตั้งค่า FRP
- Solutions อยู่ใน `/Solutions/Lab3/`

## 🎓 Tips:
- ทำทีละ Phase อย่าข้าม
- อ่าน TODO comments ทุกจุด
- ลองปรับค่าพารามิเตอร์
- บันทึกผลลัพธ์สำคัญ

---
**Created**: 2025-01-05  
**Version**: 1.0  
**Course**: DAB+ Labs for Raspberry Pi
