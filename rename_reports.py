#!/usr/bin/env python3
"""批次重新命名研究報告檔案（PDF / Word）。

命名格式：ticker_股票名稱_日期_券商名稱.ext
例如：
- 2330_台積電_20260425_元大.pdf
- NVDA_NVIDIA_20260425_Morgan Stanley.docx
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover - optional dependency runtime check
    PdfReader = None

try:
    import docx  # type: ignore
except Exception:  # pragma: no cover - optional dependency runtime check
    docx = None

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc"}

BROKER_KEYWORDS = [
    "元大", "凱基", "群益", "永豐", "富邦", "國泰", "中信", "台新", "兆豐", "第一金", "玉山", "統一",
    "Morgan Stanley", "Goldman Sachs", "J.P. Morgan", "JP Morgan", "UBS", "Citi", "Barclays",
    "BofA", "Bank of America", "Jefferies", "Deutsche Bank", "HSBC", "Nomura", "Mizuho",
]

DATE_PATTERNS = [
    re.compile(r"\b(20\d{2})([01]\d)([0-3]\d)\b"),
    re.compile(r"\b(20\d{2})[-/.]([01]?\d)[-/.]([0-3]?\d)\b"),
    re.compile(r"\b([0-3]?\d)[-/.]([01]?\d)[-/.](20\d{2})\b"),
]

# 先嘗試常見格式：2330 台積電 / NVDA NVIDIA
TICKER_NAME_PATTERNS = [
    re.compile(r"\b([0-9]{4}|[A-Z]{1,6})\s*[-_:： ]\s*([\u4e00-\u9fffA-Za-z0-9&.\- ]{2,30})"),
    re.compile(r"\(([0-9]{4}|[A-Z]{1,6})\)\s*([\u4e00-\u9fffA-Za-z0-9&.\- ]{2,30})"),
    re.compile(r"([\u4e00-\u9fffA-Za-z0-9&.\- ]{2,30})\s*\(([0-9]{4}|[A-Z]{1,6})\)"),
]


@dataclass
class ParsedMeta:
    ticker: str | None = None
    company_name: str | None = None
    date_yyyymmdd: str | None = None
    broker_name: str | None = None

    def complete(self) -> bool:
        return all([self.ticker, self.company_name, self.date_yyyymmdd, self.broker_name])


def read_pdf_text(path: Path, max_pages: int = 2) -> str:
    if PdfReader is None:
        raise RuntimeError("缺少 pypdf，請先安裝：pip install pypdf")

    reader = PdfReader(str(path))
    texts: list[str] = []
    for page in reader.pages[:max_pages]:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def read_docx_text(path: Path, max_paragraphs: int = 80) -> str:
    if docx is None:
        raise RuntimeError("缺少 python-docx，請先安裝：pip install python-docx")

    document = docx.Document(str(path))
    paragraphs = [p.text for p in document.paragraphs[:max_paragraphs]]
    return "\n".join(paragraphs)


def read_doc_text(path: Path) -> str:
    """.doc 舊格式先嘗試以純文字讀取（若失敗會回傳空字串）。"""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_date(text: str) -> str | None:
    for pattern in DATE_PATTERNS:
        for m in pattern.finditer(text):
            groups = m.groups()
            if len(groups) != 3:
                continue

            if pattern is DATE_PATTERNS[2]:
                day, month, year = groups
            else:
                year, month, day = groups

            try:
                dt = datetime(int(year), int(month), int(day))
            except ValueError:
                continue
            return dt.strftime("%Y%m%d")
    return None


def extract_broker(text: str) -> str | None:
    for broker in BROKER_KEYWORDS:
        if broker.lower() in text.lower():
            return broker
    return None


def looks_like_noise(name: str) -> bool:
    bad_words = {"buy", "hold", "sell", "research", "report", "update", "initiation", "target"}
    low = name.lower().strip()
    return low in bad_words or len(low) < 2


def clean_company_name(name: str) -> str:
    name = normalize_spaces(name)
    name = re.sub(r"\b(Buy|Hold|Sell|Research|Report|Update|Initiation)\b", "", name, flags=re.IGNORECASE)
    return normalize_spaces(name).strip("-_()[]")


def extract_ticker_and_name(text: str) -> tuple[str | None, str | None]:
    lines = [normalize_spaces(l) for l in text.splitlines() if normalize_spaces(l)]
    candidate_area = "\n".join(lines[:20])

    for pattern in TICKER_NAME_PATTERNS:
        m = pattern.search(candidate_area)
        if not m:
            continue

        g1, g2 = normalize_spaces(m.group(1)), normalize_spaces(m.group(2))
        if re.fullmatch(r"[0-9]{4}|[A-Z]{1,6}", g1):
            ticker, name = g1, clean_company_name(g2)
        else:
            ticker, name = g2, clean_company_name(g1)

        if not looks_like_noise(name):
            return ticker, name

    m = re.search(r"\b([0-9]{4}|[A-Z]{1,6})\b", candidate_area)
    ticker = m.group(1) if m else None
    return ticker, None


def parse_metadata(path: Path) -> ParsedMeta:
    text_source = path.stem

    if path.suffix.lower() == ".pdf":
        text_source += "\n" + read_pdf_text(path)
    elif path.suffix.lower() == ".docx":
        text_source += "\n" + read_docx_text(path)
    elif path.suffix.lower() == ".doc":
        text_source += "\n" + read_doc_text(path)

    text_source = normalize_spaces(text_source.replace("\u3000", " "))

    ticker, company = extract_ticker_and_name(text_source)
    date_value = extract_date(text_source)
    broker = extract_broker(text_source)

    return ParsedMeta(
        ticker=ticker,
        company_name=company,
        date_yyyymmdd=date_value,
        broker_name=broker,
    )


def sanitize_filename(value: str) -> str:
    value = value.replace("/", "-").replace("\\", "-")
    return re.sub(r"[:*?\"<>|]", "", value).strip()


def iter_documents(folder: Path) -> Iterable[Path]:
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def rename_reports(folder: Path, dry_run: bool = True, overwrite: bool = False) -> int:
    processed = 0
    for file_path in iter_documents(folder):
        processed += 1
        try:
            meta = parse_metadata(file_path)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {file_path.name}: 讀取失敗 - {exc}")
            continue

        missing = [
            k for k, v in {
                "ticker": meta.ticker,
                "股票名稱": meta.company_name,
                "日期": meta.date_yyyymmdd,
                "券商名稱": meta.broker_name,
            }.items() if not v
        ]

        if missing:
            print(f"[SKIP]  {file_path.name}: 無法完整辨識欄位 {', '.join(missing)}")
            continue

        new_base = f"{meta.ticker}_{meta.company_name}_{meta.date_yyyymmdd}_{meta.broker_name}"
        new_name = sanitize_filename(new_base) + file_path.suffix.lower()
        new_path = file_path.with_name(new_name)

        if new_path == file_path:
            print(f"[OK]    {file_path.name}: 名稱已符合規則")
            continue

        if new_path.exists() and not overwrite:
            print(f"[SKIP]  {file_path.name}: 目標檔名已存在 {new_name}")
            continue

        print(f"[RENAME] {file_path.name} -> {new_name}")
        if not dry_run:
            file_path.rename(new_path)

    return processed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="批次重新命名研究報告檔案（PDF/Word）")
    parser.add_argument("folder", nargs="?", default=".", help="目標資料夾（預設目前目錄）")
    parser.add_argument("--apply", action="store_true", help="實際執行重新命名（預設僅預覽）")
    parser.add_argument("--overwrite", action="store_true", help="若目標檔名已存在則覆蓋")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        print(f"找不到資料夾：{folder}")
        return 1

    dry_run = not args.apply
    mode = "預覽模式（不會修改檔名）" if dry_run else "執行模式（會修改檔名）"
    print(f"開始掃描：{folder} | {mode}")

    processed = rename_reports(folder=folder, dry_run=dry_run, overwrite=args.overwrite)
    print(f"完成，共處理 {processed} 個檔案。")

    if dry_run:
        print("若結果正確，請加上 --apply 來實際改名。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
