import contextlib
import html as html_module
import json
import locale
import os
import re
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Optional

# TRANSLATIONSに含まれる言語名からISO 639-1コードへのマッピング辞書
LANG_MAP = {
    "Arabic": "ar",
    "Bengali": "bn",
    "German": "de",
    "English": "en",
    "Spanish": "es",
    "Persian": "fa",
    "French": "fr",
    "Hindi": "hi",
    "Indonesian": "id",
    "Japanese": "ja",
    "Javanese": "jv",
    "Korean": "ko",
    "Marathi": "mr",
    "Malay": "ms",
    "Punjabi": "pa",
    "Portuguese": "pt",
    "Russian": "ru",
    "Swahili": "sw",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Vietnamese": "vi",
    "Chinese_China": "zh_CN",
    "Chinese_Taiwan": "zh_TW",
}

TRANSLATIONS = {
    "ar": {
        "error_lang_detection": "خطأ أثناء اكتشاف لغة النظام: {}",
        "file_not_found": "خطأ: الملف غير موجود: {}",
        "json_decode_error": "خطأ في فك ترميز JSON: {}",
        "xml_parse_error": "خطأ في تحليل XML: {}",
        "start_processing": "ðŸš€ بدء المعالجة: جاري تحميل {}...",
        "extracted_entries": "تم استخراج {0} مدخلات، منها {1} هي سجل Gemini.",
        "converting_markdown": "جاري التحويل إلى Markdown...",
        "appended_to_file": "تمت إضافة سجلات الدردشة إلى الملف: {}",
        "written_to_file": "تم كتابة سجلات الدردشة إلى الملف: {}",
        "processing_complete": "âœ… اكتمل: تم حفظ السجل من {0} إلى {1} في إجمالي {2} ملفات.",
        "error_occurred": "حدث خطأ: {}",
    },
    "bn": {
        "error_lang_detection": "সিস্টেম ভাষা সনাক্তকরণে ত্রুটি: {}",
        "file_not_found": "ত্রুটি: ফাইল পাওয়া যায়নি: {}",
        "json_decode_error": "JSON ডিকোড ত্রুটি: {}",
        "xml_parse_error": "XML পার্স ত্রুটি: {}",
        "start_processing": "ðŸš€ প্রক্রিয়াকরণ শুরু হচ্ছে: {} লোড হচ্ছে...",     
        "extracted_entries": "{0} এন্ট্রি বের করা হয়েছে, যার মধ্যে {1} টি Gemini ইতিহাস।",
        "converting_markdown": "Markdown এ রূপান্তর করা হচ্ছে...",
        "appended_to_file": "চ্যাট ইতিহাস ফাইলে যোগ করা হয়েছে: {}",
        "written_to_file": "চ্যাট ইতিহাস ফাইলে লেখা হয়েছে: {}",
        "processing_complete": "âœ… সম্পন্ন: {0} থেকে {1} পর্যন্ত ইতিহাস মোট {2} ফাইলে সংরক্ষণ করা হয়েছে।",
        "error_occurred": "একটি ত্রুটি ঘটেছে: {}",
    },
    "de": {
        "error_lang_detection": "Fehler bei der Erkennung der Systemsprache: {}",
        "file_not_found": "Fehler: Datei nicht gefunden: {}",
        "json_decode_error": "JSON-Decodierungsfehler: {}",
        "xml_parse_error": "XML-Parse-Fehler: {}",
        "start_processing": "ðŸš€ Verarbeitung gestartet: Lade {}...",
        "extracted_entries": "{0} Einträge extrahiert, davon sind {1} Gemini-Verlauf.",
        "converting_markdown": "Konvertiere zu Markdown...",
        "appended_to_file": "Chatverläufe an Datei angehängt: {}",
        "written_to_file": "Chatverläufe in Datei geschrieben: {}",
        "processing_complete": "âœ… Abgeschlossen: Verlauf von {0} bis {1} in insgesamt {2} Dateien gespeichert.",
        "error_occurred": "Ein Fehler ist aufgetreten: {}",
    },
    "en": {
        "error_lang_detection": "Error while detecting system language: {}",
        "file_not_found": "Error: File not found: {}",
        "json_decode_error": "JSON decode error: {}",
        "xml_parse_error": "XML parse error: {}",
        "start_processing": "ðŸš€ Starting processing: Loading {}...",
        "extracted_entries": "Extracted {0} entries, of which {1} are Gemini history.",
        "converting_markdown": "Converting to Markdown...",
        "appended_to_file": "Chat histories appended to file: {}",
        "written_to_file": "Chat histories written to file: {}",
        "processing_complete": "âœ… Completed: Saved history after {0} to {1} into a total of {2} files.",
        "error_occurred": "An error occurred: {}",
    },
    "es": {
        "error_lang_detection": "Error al detectar el idioma del sistema: {}",
        "file_not_found": "Error: Archivo no encontrado: {}",
        "json_decode_error": "Error al decodificar JSON: {}",
        "xml_parse_error": "Error de análisis XML: {}",
        "start_processing": "ðŸš€ Iniciando procesamiento: Cargando {}...",
        "extracted_entries": "Se extrajeron {0} entradas, de las cuales {1} son historial de Gemini.",
        "converting_markdown": "Convirtiendo a Markdown...",
        "appended_to_file": "Historiales de chat agregados al archivo: {}",
        "written_to_file": "Historiales de chat escritos en el archivo: {}",
        "processing_complete": "âœ… Completado: Historial guardado desde {0} hasta {1} en un total de {2} archivos.",
        "error_occurred": "Ocurrió un error: {}",
    },
    "fa": {
        "error_lang_detection": "خطا در شناسایی زبان سیستم: {}",
        "file_not_found": "خطا: فایل پیدا نشد: {}",
        "json_decode_error": "خطای رمزگشایی JSON: {}",
        "xml_parse_error": "خطای تجزیه XML: {}",
        "start_processing": "ðŸš€ شروع پردازش: در حال بارگذاری {}...",
        "extracted_entries": "{0} ورودی استخراج شد که {1} مورد از آنها تاریخچه Gemini است.",     
        "converting_markdown": "در حال تبدیل به Markdown...",
        "appended_to_file": "تاریخچه چت به فایل اضافه شد: {}",
        "written_to_file": "تاریخچه چت در فایل نوشته شد: {}",
        "processing_complete": "âœ… تکمیل شد: تاریخچه از {0} تا {1} در مجموع در {2} فایل ذخیره شد.",
        "error_occurred": "یک خطا رخ داد: {}",
    },
    "fr": {
        "error_lang_detection": "Erreur lors de la détection de la langue du système : {}",
        "file_not_found": "Erreur : Fichier non trouvé : {}",
        "json_decode_error": "Erreur de décodage JSON : {}",
        "xml_parse_error": "Erreur d'analyse XML : {}",
        "start_processing": "ðŸš€ Démarrage du traitement : Chargement de {}...",
        "extracted_entries": "{0} entrées extraites, dont {1} sont l'historique Gemini.",
        "converting_markdown": "Conversion en Markdown...",
        "appended_to_file": "Historiques de chat ajoutés au fichier : {}",
        "written_to_file": "Historiques de chat écrits dans le fichier : {}",
        "processing_complete": "âœ… Terminé : Historique sauvegardé de {0} à {1} dans un total de {2} fichiers.",
        "error_occurred": "Une erreur est survenue : {}",
    },
    "hi": {
        "error_lang_detection": "त्रुटि: सिस्टम भाषा का पता लगाने में समस्या: {}",
        "file_not_found": "त्रुटि: फ़ाइल नहीं मिली: {}",
        "json_decode_error": "JSON डिकोड त्रुटि: {}",
        "xml_parse_error": "XML पार्स त्रुटि: {}",
        "start_processing": "ðŸš€ प्रसंस्करण शुरू हो रहा है: {} लोड हो रहा है...",
        "extracted_entries": "Ditemukan {0} entri, di mana {1} adalah riwayat Gemini.",
        "converting_markdown": "Mengonversi ke Markdown...",
        "appended_to_file": "Riwayat obrolan ditambahkan ke file: {}",
        "written_to_file": "Riwayat obrolan ditulis ke file: {}",
        "processing_complete": "âœ… Selesai: Riwayat disimpan dari {0} hingga {1} dalam total {2} file.",
        "error_occurred": "Terjadi kesalahan: {}",
    },
    "id": {
        "error_lang_detection": "Error saat mendeteksi bahasa sistem: {}",
        "file_not_found": "Error: File tidak ditemukan: {}",
        "json_decode_error": "Error decode JSON: {}",
        "xml_parse_error": "Error parse XML: {}",
        "start_processing": "ðŸš€ Memulai pemrosesan: Memuat {}...",
        "extracted_entries": "Estratti {0} voci, di cui {1} sono cronologia di Gemini.",
        "converting_markdown": "Conversione in Markdown...",
        "appended_to_file": "Cronologia chat aggiunta al file: {}",
        "written_to_file": "Cronologia chat scritta nel file: {}",
        "processing_complete": "âœ… Completato: Cronologia salvata da {0} a {1} in un totale di {2} file.",
        "error_occurred": "Si è verificato un errore: {}",
    },
    "ja": {
        "error_lang_detection": "システム言語の検出中にエラーが発生しました: {}",
        "file_not_found": "エラー: ファイルが見つかりません: {}",
        "json_decode_error": "JSONデコードエラー: {}",
        "xml_parse_error": "XMLパースエラー: {}",
        "start_processing": "ðŸš€ 処理開始: {} を読み込み中...",
        "extracted_entries": "{0} 件抽出され、うち Gemini の履歴は {1} 件ありました。",
        "converting_markdown": "Markdown に変換中...",
        "appended_to_file": "チャット履歴をファイルに追記しました: {}",
        "written_to_file": "チャット履歴をファイルに書き込みました: {}",
        "processing_complete": "âœ… 完了しました: {0} より後の {1} までの履歴を延べ {2} ファイルに分割保存しました。", 
        "error_occurred": "エラーが発生しました: {}",
    },
    "jv": {
        "error_lang_detection": "Kesalahan saat mendeteksi bahasa sistem: {}",
        "file_not_found": "Kesalahan: Berkas tidak ditemukan: {}",
        "json_decode_error": "Kesalahan dekode JSON: {}",
        "xml_parse_error": "Kesalahan parse XML: {}",
        "start_processing": "ðŸš€ Memulai pemrosesan: Memuat {}...",
        "extracted_entries": "Ditemukan {0} entri, di mana {1} adalah riwayat Gemini.",
        "converting_markdown": "Mengonversi ke Markdown...",
        "appended_to_file": "Riwayat obrolan ditambahkan ke berkas: {}",
        "written_to_file": "Riwayat obrolan ditulis ke berkas: {}",
        "processing_complete": "âœ… Selesai: Riwayat disimpan dari {0} hingga {1} dalam total {2} berkas.",
        "error_occurred": "Terjadi kesalahan: {}",
    },
    "ko": {
        "error_lang_detection": "시스템 언어 설정 감지 중 오류 발생: {}",
        "file_not_found": "오류: 파일을 찾을 수 없습니다: {}",
        "json_decode_error": "JSON 디코드 오류: {}",
        "xml_parse_error": "XML 파스 오류: {}",
        "start_processing": "ðŸš€ 처리 시작: {} 로드 중...",
        "extracted_entries": "{0}개의 항목이 추출되었고, 그 중 {1}개는 Gemini 기록입니다.",
        "converting_markdown": "Markdown으로 변환 중...",
        "appended_to_file": "채팅 기록이 파일에 추가되었습니다: {}",
        "written_to_file": "채팅 기록이 파일에 작성되었습니다: {}",
        "processing_complete": "âœ… 완료: {0}부터 {1}까지의 기록이 총 {2}개의 파일에 저장되었습니다.",
        "error_occurred": "오류가 발생했습니다: {}",
    },
    "mr": {
        "error_lang_detection": "त्रुटी: सिस्टम भाषा ओळखण्यात समस्या: {}",       
        "file_not_found": "त्रुटी: फाइल सापडली नाही: {}",
        "json_decode_error": "JSON डिकोड त्रुटी: {}",
        "xml_parse_error": "XML पार्स त्रुटी: {}",
        "start_processing": "ðŸš€ प्रक्रिया सुरू होत आहे: {} लोड होत आहे...",
        "extracted_entries": "{0} नोंदी काढल्या, ज्यापैकी {1} Gemini इतिहास आहे.",
        "converting_markdown": "Markdown मध्ये रूपांतरित करत आहे...",
        "appended_to_file": "चॅट इतिहास फाइलमध्ये जोडला गेला: {}",
        "written_to_file": "चॅट इतिहास फाइलमध्ये लिहिला गेला: {}",
        "processing_complete": "âœ… पूर्ण झाले: इतिहास {0} पासून {1} पर्यंत एकूण {2} फाइल्समध्ये जतन केला गेला.",
        "error_occurred": "एक त्रुटी आली आहे: {}",
    },
    "ms": {
        "error_lang_detection": "Ralat semasa mengesan bahasa sistem: {}",
        "file_not_found": "Ralat: Fail tidak dijumpai: {}",
        "json_decode_error": "Ralat nyahkod JSON: {}",
        "xml_parse_error": "Ralat huraian XML: {}",
        "start_processing": "ðŸš€ Memulakan pemprosesan: Memuat {}...",
        "extracted_entries": "Diekstrak {0} entri, di mana {1} adalah sejarah Gemini.",
        "converting_markdown": "Menukar kepada Markdown...",
        "appended_to_file": "Sejarah sembang ditambah ke fail: {}",
        "written_to_file": "Sejarah sembang ditulis ke fail: {}",
        "processing_complete": "âœ… Selesai: Sejarah disimpan dari {0} hingga {1} dalam jumlah {2} fail.",
        "error_occurred": "Ralat telah berlaku: {}",
    },
    "pa": {
        "error_lang_detection": "ਸਿਸਟਮ ਭਾਸ਼ਾ ਦਾ ਪਤਾ ਲਗਾਉਣ ਸਮੇਂ ਤਰੁੱਟੀ: {}",
        "file_not_found": "ਤਰੁੱਟੀ: ਫਾਈਲ ਨਹੀਂ ਮਿਲੀ: {}",
        "json_decode_error": "JSON ਡੀਕੋਡ ਤਰੁੱਟੀ: {}",
        "xml_parse_error": "XML ਪਾਰਸ ਤਰੁੱਟੀ: {}",
        "start_processing": "ðŸš€ ਪ੍ਰਕਿਰਿਆ ਸ਼ੁਰੂ ਹੋ ਰਹੀ ਹੈ: {} ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...",
        "extracted_entries": "{0} ਐਂਟਰੀਆਂ ਨਿਕਾਲੀਆਂ ਗਈਆਂ, ਜਿਨ੍ਹਾਂ ਵਿੱਚੋਂ {1} Gemini ਇਤਿਹਾਸ ਹੈ।",
        "converting_markdown": "Markdown ਵਿੱਚ ਬਦਲ ਰਿਹਾ ਹੈ...",
        "appended_to_file": "ਚੈਟ ਇਤਿਹਾਸ ਫਾਈਲ ਵਿੱਚ ਸ਼ਾਮਲ ਕੀਤਾ ਗਿਆ: {}",        
        "written_to_file": "ਚੈਟ ਇਤਿਹਾਸ ਫਾਈਲ ਵਿੱਚ ਲਿਖਿਆ ਗਿਆ: {}",
        "processing_complete": "âœ… ਮੁਕੰਮਲ: ਇਤਿਹਾਸ {0} ਤੋਂ {1} ਤੱਕ ਕੁੱਲ {2} ਫਾਈਲਾਂ ਵਿੱਚ ਸੁਰੱਖਿਅਤ ਕੀਤਾ ਗਿਆ।",
        "error_occurred": "ਇੱਕ ਤਰੁੱਟੀ ਆਈ: {}",
    },
    "pt": {
        "error_lang_detection": "Erro ao detectar o idioma do sistema: {}",
        "file_not_found": "Erro: Arquivo não encontrado: {}",
        "json_decode_error": "Erro de decodificação JSON: {}",
        "xml_parse_error": "Erro de análise XML: {}",
        "start_processing": "ðŸš€ Iniciando processamento: Carregando {}...",
        "extracted_entries": "Extraídas {0} entradas, das quais {1} são histórico do Gemini.",
        "converting_markdown": "Convertendo para Markdown...",
        "appended_to_file": "Históricos de chat adicionados ao arquivo: {}",
        "written_to_file": "Históricos de chat escritos no arquivo: {}",
        "processing_complete": "âœ… Concluído: Histórico salvo de {0} a {1} em um total de {2} arquivos.",
        "error_occurred": "Ocorreu um erro: {}",
    },
    "ru": {
        "error_lang_detection": "Ошибка при определении языка системы: {}",
        "file_not_found": "Ошибка: Файл не найден: {}",
        "json_decode_error": "Ошибка декодирования JSON: {}",
        "xml_parse_error": "Ошибка синтаксического анализа XML: {}",
        "start_processing": "ðŸš€ Начало обработки: Загрузка {}...",
        "extracted_entries": "Извлечено {0} записей, из которых {1} относятся к истории Gemini.",   
        "converting_markdown": "Преобразование в Markdown...",
        "appended_to_file": "История чата добавлена в файл: {}",
        "written_to_file": "История чата записана в файл: {}",
        "processing_complete": "âœ… Завершено: История сохранена с {0} по {1} в общей сложности в {2} файлах.",
        "error_occurred": "Произошла ошибка: {}",
    },
    "sw": {
        "error_lang_detection": "Hitilafu wakati wa kugundua lugha ya mfumo: {}",
        "file_not_found": "Hitilafu: Faili haikupatikana: {}",
        "json_decode_error": "Hitilafu ya kutafsiri JSON: {}",
        "xml_parse_error": "Hitilafu ya kuchanganua XML: {}",
        "start_processing": "ðŸš€ Kuanzia usindikaji: Inapakia {}...",
        "extracted_entries": "Imechota rekodi {0}, ambapo {1} ni historia ya Gemini.",
        "converting_markdown": "Inabadilisha kuwa Markdown...",
        "appended_to_file": "Historia za mazungumzo zimeongezwa kwenye faili: {}",
        "written_to_file": "Historia za mazungumzo zimeandikwa kwenye faili: {}",
        "processing_complete": "âœ… Imekamilika: Historia imehifadhiwa kutoka {0} hadi {1} katika jumla ya faili {2}.",
        "error_occurred": "Hitilafu imetokea: {}",
    },
    "ta": {
        "error_lang_detection": "சிஸ்டம் மொழியை கண்டறிதலில் பிழை: {}",
        "file_not_found": "பிழை: கோப்பு காணப்படவில்லை: {}",
        "json_decode_error": "JSON குறியாக்கி பிழை: {}",
        "xml_parse_error": "XML பாகுபடுத்தல் பிழை: {}",
        "start_processing": "ðŸš€ செயலாக்கம் தொடங்குகிறது: {} ஏற்றப்படுகிறது...",
        "extracted_entries": "à¸”à¸¶à¸‡à¸‚à¹‰à¸­à¸¡à¸¹à¸¥ {0} à¸£à¸²à¸¢à¸à¸²à¸£ à¸‹à¸¶à¹ˆà¸‡à¸¡à¸µà¸›à¸£à¸°à¸§à¸±à¸•à¸´à¸‚à¸­à¸‡ Gemini à¸ˆà¸³à¸™à¸§à¸™ {1} à¸£à¸²à¸¢à¸à¸²à¸£",
        "converting_markdown": "à¸à¸³à¸¥à¸±à¸‡à¹à¸›à¸¥à¸‡à¹€à¸›à¹‡à¸™ Markdown...",
        "appended_to_file": "à¸›à¸£à¸°à¸§à¸±à¸•à¸´à¸à¸²à¸£à¹à¸Šà¸—à¸–à¸¹à¸à¹€à¸žà¸´à¹ˆà¸¡à¸¥à¸‡à¹ƒà¸™à¹„à¸Ÿà¸¥à¹Œ: {}",
        "written_to_file": "à¸›à¸£à¸°à¸§à¸±à¸•à¸´à¸à¸²à¸£à¹à¸Šà¸—à¸–à¸¹à¸à¹€à¸‚à¸µà¸¢à¸™à¸¥à¸‡à¹ƒà¸™à¹„à¸Ÿà¸¥à¹Œ: {}",
        "processing_complete": "âœ… à¹€à¸ªà¸£à¹‡à¸ˆà¸ªà¸´à¹‰à¸™: à¸šà¸±à¸™à¸—à¸¶à¸à¸›à¸£à¸°à¸§à¸±à¸•à¸´à¸ˆà¸²à¸ {0} à¸–à¸¶à¸‡ {1} à¸¥à¸‡à¹ƒà¸™à¹„à¸Ÿà¸¥à¹Œà¸—à¸±à¹‰à¸‡à¸«à¸¡à¸” {2} à¹„à¸Ÿà¸¥à¹Œ",
        "error_occurred": "à¹€à¸à¸´à¸”à¸‚à¹‰à¸­à¸œà¸´à¸”à¸žà¸¥à¸²à¸”: {}",
    },
    "te": {
        "error_lang_detection": "సిస్టమ్ భాషను గుర్తించడంలో లోపం: {}",
        "file_not_found": "లోపం: ఫైల్ కనుగొనబడలేదు: {}",
        "json_decode_error": "JSON డీకోడ్ లోపం: {}",
        "xml_parse_error": "XML పార్సింగ్ లోపం: {}",
        "start_processing": "ðŸš€ ప్రాసెసింగ్ ప్రారంభం: {} లోడ్ అవుతోంది...",  
        "extracted_entries": "{0} ఎంట్రీలు తీసుకోబడ్డాయి, వాటిలో {1} జెమిని చరిత్ర.",
        "converting_markdown": "Markdown కు మారుస్తోంది...",
        "appended_to_file": "చాట్ చరిత్ర ఫైల్‌కు జోడించబడింది: {}",
        "written_to_file": "చాట్ చరిత్ర ఫైల్‌కు రాయబడింది: {}",
        "processing_complete": "âœ… పూర్తయింది: చరిత్ర {0} నుండి {1} వరకు మొత్తం {2} ఫైళ్ళలో సేవ్ చేయబడింది.",
        "error_occurred": "లోపం సంభవించింది: {}",
    },
    "th": {
        "error_lang_detection": "เกิดข้อผิดพลาดขณะตรวจจับภาษาของระบบ: {}",  
        "file_not_found": "ข้อผิดพลาด: ไม่พบไฟล์: {}",
        "json_decode_error": "ข้อผิดพลาดในการถอดรหัส JSON: {}",
        "xml_parse_error": "ข้อผิดพลาดในการแยกวิเคราะห์ XML: {}",
        "start_processing": "ðŸš€ เริ่มการประมวลผล: กำลังโหลด {}...",
        "extracted_entries": "ดึงข้อมูล {0} รายการ ซึ่งมีประวัติของ Gemini จำนวน {1} รายการ",
        "converting_markdown": "กำลังแปลงเป็น Markdown...",
        "appended_to_file": "ประวัติการแชทถูกเพิ่มลงในไฟล์: {}",
        "written_to_file": "ประวัติการแชทถูกเขียนลงในไฟล์: {}",
        "processing_complete": "âœ… เสร็จสิ้น: บันทึกประวัติจาก {0} ถึง {1} ลงในไฟล์ทั้งหมด {2} ไฟล์",
        "error_occurred": "เกิดข้อผิดพลาด: {}",
    },
    "tr": {
        "error_lang_detection": "Sistem dili algılanırken hata oluştu: {}",
        "file_not_found": "Hata: Dosya bulunamadı: {}",
        "json_decode_error": "JSON kod çözme hatası: {}",
        "xml_parse_error": "XML ayrıştırma hatası: {}",
        "start_processing": "ðŸš€ İşleme başlıyor: {} yükleniyor...",
        "extracted_entries": "{0} giriş çıkarıldı, bunların {1} tanesi Gemini geçmişi.",
        "converting_markdown": "Markdown'a dönüştürülüyor...",
        "appended_to_file": "Sohbet geçmişi dosyaya eklendi: {}",
        "written_to_file": "Sohbet geçmişi dosyaya yazıldı: {}",
        "processing_complete": "âœ… Tamamlandı: {0} ile {1} arasındaki geçmiş toplam {2} dosyaya kaydedildi.",
        "error_occurred": "Bir hata oluştu: {}",
    },
    "uk": {
        "error_lang_detection": "Помилка під час визначення мови системи: {}",
        "file_not_found": "Помилка: Файл не знайдено: {}",
        "json_decode_error": "Помилка декодування JSON: {}",
        "xml_parse_error": "Помилка синтаксичного аналізу XML: {}",
        "start_processing": "ðŸš€ Початок обробки: Завантаження {}...",
        "extracted_entries": "Вилучено {0} записів, з яких {1} стосуються історії Gemini.",
        "converting_markdown": "Конвертація в Markdown...",
        "appended_to_file": "Історія чату додана до файлу: {}",
        "written_to_file": "Історія чату записана у файл: {}",
        "processing_complete": "âœ… Завершено: Історія з {0} по {1} збережена усього в {2} файлах.",
        "error_occurred": "Сталася помилка: {}",
    },
    "ur": {
        "error_lang_detection": "سسٹم زبان کا پتہ لگانے میں خرابی: {}",
        "file_not_found": "خرابی: فائل نہیں ملی: {}",
        "json_decode_error": "JSON ڈی کوڈنگ کی خرابی: {}",
        "xml_parse_error": "XML پارسنگ کی خرابی: {}",
        "start_processing": "ðŸš€ پراسیسنگ شروع ہو رہی ہے: {} لوڈ ہو رہا ہے...",
        "extracted_entries": "{0} اندراجات نکالے گئے، جن میں سے {1} Gemini کی تاریخ ہے",
        "converting_markdown": "Markdown میں تبدیل کیا جا رہا ہے...",
        "appended_to_file": "چیٹ کی تاریخ فائل میں شامل کر دی گئی ہے: {}",
        "written_to_file": "چیٹ کی تاریخ فائل میں لکھ دی گئی ہے: {}",
        "processing_complete": "âœ… مکمل ہو گیا: تاریخ {0} سے {1} تک کل {2} فائلوں میں محفوظ کر دی گئی ہے",
        "error_occurred": "ایک خرابی پیش آئی: {}",
    },
    "vi": {
        "error_lang_detection": "Lỗi khi phát hiện ngôn ngữ hệ thống: {}",
        "file_not_found": "Lỗi: Không tìm thấy tệp: {}",
        "json_decode_error": "Lỗi giải mã JSON: {}",
        "xml_parse_error": "Lỗi phân tích XML: {}",
        "start_processing": "ðŸš€ Bắt đầu xử lý: Đang tải {}...",
        "extracted_entries": "Đã trích xuất {0} mục, trong đó có {1} là lịch sử Gemini.",
        "converting_markdown": "Đang chuyển đổi sang Markdown...",
        "appended_to_file": "Lịch sử trò chuyện đã được thêm vào tệp: {}",
        "written_to_file": "Lịch sử trò chuyện đã được ghi vào tệp: {}",
        "processing_complete": "âœ… Hoàn thành: Đã lưu lịch sử từ {0} đến {1} vào tổng cộng {2} tệp.",
        "error_occurred": "Đã xảy ra lỗi: {}",
    },
    "zh_CN": {
        "error_lang_detection": "检测系统语言时出错：{}",
        "file_not_found": "错误：未找到文件：{}",
        "json_decode_error": "JSON 解码错误：{}",
        "xml_parse_error": "XML 解析错误：{}",
        "start_processing": "ðŸš€ 开始处理：正在加载 {}...",
        "extracted_entries": "提取了 {0} 条项目，其中 {1} 条是 Gemini 历史记录。",
        "converting_markdown": "正在转换为 Markdown...",
        "appended_to_file": "聊天历史已追加到文件：{}",
        "written_to_file": "聊天历史已写入文件：{}",
        "processing_complete": "âœ… 完成：已将 {0} 到 {1} 之间的历史记录保存到共计 {2} 个文件中。",
        "error_occurred": "发生错误：{}",
    },
    "zh_TW": {
        "error_lang_detection": "偵測系統語言時出錯：{}",
        "file_not_found": "錯誤：未找到檔案：{}",
        "json_decode_error": "JSON 解碼錯誤：{}",
        "xml_parse_error": "XML 解析錯誤：{}",
        "start_processing": "ðŸš€ 開始處理：正在載入 {}...",
        "extracted_entries": "擷取了 {0} 條項目，其中 {1} 條是 Gemini 歷史記錄。",
        "converting_markdown": "正在轉換為 Markdown...",
        "appended_to_file": "聊天歷史已追加到檔案：{}",
        "written_to_file": "聊天歷史已寫入檔案：{}",
        "processing_complete": "âœ… 完成：已將 {0} 到 {1} 之間的歷史記錄儲存到共計 {2} 個檔案中。",
        "error_occurred": "發生錯誤：{}",
    },
}


def get_system_language() -> str:
    """detect OS language setting"""
    try:
        lang_tuple = locale.getlocale()
        if lang_tuple[0]:
            lang_name = lang_tuple[0].split("_")[0]
            lang_code = LANG_MAP.get(lang_name, lang_name[:2].lower())
        else:
            lang_code = None

        if lang_code is None:
            return "en"

        if lang_code == "zh_CN" or lang_code == "zh-Hans" or lang_name == "Chinese_China":
            return "zh_CN"
        elif lang_code == "zh_TW" or lang_code == "zh-Hant" or lang_name == "Chinese_Taiwan":
            return "zh_TW"

        lang_code = lang_code.split("_")[0].split("-")[0].lower()
        if lang_code in TRANSLATIONS:
            return lang_code
        return "en"

    except Exception as e:
        error_msg = TRANSLATIONS.get("en", {}).get("error_lang_detection", "Error: {}")
        print(error_msg.format(e))
        return "en"


def t(key: str, *args: Any) -> str:
    """Translation function"""
    lang = get_system_language()

    msg_map: dict[str, str] = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    msg: str = msg_map.get(key, TRANSLATIONS["en"].get(key, key))

    if args:
        try:
            return msg.format(*args)
        except IndexError:
            # Safety measure in case the number of placeholders and variables do not match
            return msg
    return msg

def select_xml_file() -> Optional[str]:
    """
    ファイル選択ダイアログを表示し、ユーザーが選択したXMLファイルのパスを返します。
    キャンセルされた場合はNoneを返します。
    """
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示にする
    file_path = filedialog.askopenfilename(
        title="処理するXMLファイルを選択してください",
        filetypes=[("XML files", "*.xml"), ("すべてのファイル", "*.*")]
    )
    root.destroy()
    return file_path

def load_xml(filepath: str) -> Any:
    """Load an XML file and return the root element."""
    if not os.path.exists(filepath):
        print(t("file_not_found", filepath))
        return None

    with open(filepath, 'rb') as f:
        raw_bytes = f.read()

    decoded_content = None
    try:
        decoded_content = raw_bytes.decode('shift-jis')
    except UnicodeDecodeError:
        try:
            decoded_content = raw_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            print(t("xml_parse_error", f"UnicodeDecodeError: {e}"))
            return None

    if decoded_content:
        try:
            root = ET.fromstring(decoded_content)
            return root
        except ET.ParseError as e:
            print(t("xml_parse_error", f"XML parse error after decoding: {e}"))
            return None
    return None

def decode_unicode_escapes(s: str) -> str:
    """Decode Unicode escape sequences"""

    def repl(match):
        return chr(int(match.group(1), 16))

    return re.sub(r"\u([0-9a-fA-F]{4})", repl, s)


def html_to_markdown(html_str: str) -> str:
    """
    Simple HTML -> Markdown/Text conversion
    Remove HTML tags and format into readable text
    """
    if not html_str:
        return ""

    text = decode_unicode_escapes(html_str)
    text = html_module.unescape(text)

    # Replace major tags (h1-h6, li, p, div, br, b, strong) with Markdown-like symbols and line breaks
    # Headings (h1-h6) -> **Heading** + line break
    text = re.sub(r"<h[1-6][^>]*>(.*?)</h[1-6]>", r"
**\1**
", text, flags=re.IGNORECASE)

    # List items (li) -> - + line break
    text = re.sub(r"<li[^>]*>", r"
- ", text, flags=re.IGNORECASE)

    # Paragraphs (p), line breaks (div), line breaks (br) -> line breaks
    text = re.sub(r"</p>", r"

", text, flags=re.IGNORECASE)
    text = re.sub(r"</div>", r"
", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", r"
", text, flags=re.IGNORECASE)

    # Bold (b, strong) -> **text**
    text = re.sub(r"<(b|strong)[^>]*>(.*?)</\1>", r"**\2**", text, flags=re.IGNORECASE)

    # Remove all other HTML tags (keep the content)
    text = re.sub(r"<[^>]+>", "", text)

    # Organize consecutive blank lines (reduce 3 or more line breaks to 2)
    text = re.sub(r"
{3,}", "

", text)

    return text.strip()


def extract_text_content(entry_element: ET.Element, last_entry_time_loaded: datetime) -> tuple[datetime, str]:
    """Extract Markdown-formatted text content from an XML entry element"""

    # Extracting publish date
    pub_date_element = entry_element.find("pubDate")
    time_str = pub_date_element.text if pub_date_element is not None else ""

    dt: datetime = datetime.min.replace(tzinfo=timezone.utc)  # Default value
    try:
        # pubDate format is like 'Wed, 11 Feb 2026 14:50:38 +0900'
        if time_str:
            dt = datetime.strptime(time_str, "%a, %d %b %Y %H:%M:%S %z")
        if dt <= last_entry_time_loaded:
            return dt, ""  # Skip already processed entries
        formatted_date = dt.strftime("%Y/%m/%d %H:%M:%S")
    except ValueError:
        formatted_date = time_str if time_str else "Unknown Date"

    md_output = f"## {formatted_date}

"

    # 1. Title
    title_element = entry_element.find("title")
    title = title_element.text if title_element is not None else ""
    if title:
        md_output += f"**Title**: {title}

"

    # 2. Content (from content:encoded, handling CDATA and HTML)
    content_encoded_element = entry_element.find("{http://purl.org/rss/1.0/modules/content/}encoded")
    html_content = content_encoded_element.text if content_encoded_element is not None else ""

    if html_content:
        converted_text = html_to_markdown(html_content)
        if converted_text.strip():
            md_output += f"{converted_text}

"

    md_output += "---

"  # Separator
    return dt, md_output
