#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tải font DejaVu Sans tự động cho game
"""

import os
import urllib.request
import zipfile

def download_font():
    print("="*70)
    print("TẢI FONT TIẾNG VIỆT TỰ ĐỘNG")
    print("="*70)
    print()
    
    # Tạo thư mục fonts
    if not os.path.exists('fonts'):
        os.makedirs('fonts')
        print("✓ Tạo thư mục fonts/")
    
    font_path = 'fonts/DejaVuSans.ttf'
    
    # Kiểm tra đã có font chưa
    if os.path.exists(font_path):
        print(f"✓ Font đã tồn tại: {font_path}")
        print("✓ HOÀN TẤT!")
        print()
        return True
    
    print("Đang tải DejaVu Sans font...")
    print("URL: https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip")
    print()
    
    try:
        # Download file
        url = "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip"
        zip_path = "fonts/dejavu.zip"
        
        print("Đang tải... (khoảng 5MB)")
        urllib.request.urlretrieve(url, zip_path)
        print("✓ Tải xong!")
        print()
        
        # Giải nén
        print("Đang giải nén...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Chỉ giải nén file DejaVuSans.ttf
            for file in zip_ref.namelist():
                if file.endswith('DejaVuSans.ttf'):
                    zip_ref.extract(file, 'fonts/')
                    # Di chuyển file
                    extracted_path = os.path.join('fonts', file)
                    os.rename(extracted_path, font_path)
                    print(f"✓ Giải nén: {font_path}")
                    break
        
        # Xóa file zip
        os.remove(zip_path)
        print("✓ Dọn dẹp file tạm")
        
        # Xóa thư mục rỗng
        try:
            extracted_dir = os.path.join('fonts', 'dejavu-fonts-ttf-2.37')
            if os.path.exists(extracted_dir):
                import shutil
                shutil.rmtree(extracted_dir)
        except:
            pass
        
        print()
        print("="*70)
        print("✅ CÀI ĐẶT FONT THÀNH CÔNG!")
        print("="*70)
        print(f"Font lưu tại: {os.path.abspath(font_path)}")
        print()
        print("Bây giờ chạy: python main.py")
        print("="*70)
        print()
        
        return True
        
    except Exception as e:
        print()
        print("="*70)
        print(f"❌ LỖI: {e}")
        print("="*70)
        print()
        print("Cài thủ công:")
        print("1. Tải: https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip")
        print("2. Giải nén")
        print("3. Copy file 'DejaVuSans.ttf' vào thư mục 'fonts/'")
        print()
        return False

if __name__ == "__main__":
    download_font()