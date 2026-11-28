#!/usr/bin/env python3
"""Pure-stdlib + optional Office-ready CHINT catalogue proofreading & PDF annotation engine.

Supports 100% standalone operation AND automatic sibling synergy:
- Prefers sibling `chint-office-suite` for Office extraction & PDF annotation when installed;
  otherwise runs built-in extractors (.pdf/.docx/.xlsx) and non-destructive PDF annotator.
- Prefers sibling `chint-translation` for IEC/GB rules & EN blacklist when installed;
  otherwise falls back to BUILTIN_SSOT_FALLBACK (parity-verified by --self-test).
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

LOW_TEXT_THRESHOLD = 50
YELLOW = (1.0, 0.92, 0.23)


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdio streams so piped JSON/text works on Windows cp936 consoles."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


# ---------------------------------------------------------------------------
# Environment & Sibling Skill Resolution
# ---------------------------------------------------------------------------

def _probe_module(mod_name: str, dist_name: str) -> dict[str, object]:
    if importlib.util.find_spec(mod_name) is None:
        return {"available": False, "version": None}
    try:
        mod = __import__(mod_name)
        ver = getattr(mod, "__version__", None)
        if mod_name == "fitz" and hasattr(mod, "VersionBind"):
            ver = str(mod.VersionBind)
        elif not isinstance(ver, str) or len(ver) > 40:
            ver = None
        if not ver:
            try:
                ver = importlib.metadata.version(dist_name)
            except importlib.metadata.PackageNotFoundError:
                ver = None
        return {"available": True, "version": str(ver) if ver else None}
    except Exception:
        return {"available": False, "version": None}


def resolve_sibling_skill(skill_name: str, sentinel_rel: str, explicit_dir: str | None = None) -> Path | None:
    if explicit_dir is not None:
        cand = Path(explicit_dir).expanduser()
        return cand if (cand / sentinel_rel).is_file() else None
    skill_root = Path(__file__).resolve().parent.parent
    candidates = [
        skill_root.parent / skill_name,
        Path.home() / ".skills-manager" / "skills" / skill_name,
    ]
    for cand in candidates:
        if (cand / sentinel_rel).is_file():
            return cand
    return None


def resolve_translation_skill(explicit_dir: str | None = None) -> Path | None:
    return resolve_sibling_skill("chint-translation", "scripts/lint_text.py", explicit_dir)


def resolve_office_skill(explicit_dir: str | None = None) -> Path | None:
    return resolve_sibling_skill("chint-office-suite", "scripts/extract_doc.py", explicit_dir)


def check_env(office_dir: str | None = None, translation_dir: str | None = None) -> dict[str, object]:
    deps = {
        "pymupdf": _probe_module("fitz", "pymupdf"),
        "openpyxl": _probe_module("openpyxl", "openpyxl"),
    }
    off = resolve_office_skill(office_dir)
    trn = resolve_translation_skill(translation_dir)
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": sys.platform,
        "standalone_ready_for_text_and_docx": True,
        "standalone_ready_for_pdf_and_xlsx": all(bool(v["available"]) for v in deps.values()),
        "dependencies": deps,
        "siblings": {
            "chint-office-suite": str(off) if off else None,
            "chint-translation": str(trn) if trn else None,
        },
        "ready": all(bool(v["available"]) for v in deps.values()),
    }


# ---------------------------------------------------------------------------
# Built-in SSOT Fallback (parity-checked against chint-translation in --self-test)
# ---------------------------------------------------------------------------

BUILTIN_SSOT_FALLBACK: dict[str, object] = {
    "BLACKLIST_COMMON": [
        (r"\bshunting release\b", "Shunt release (SHT)"),
        (r"\bshunt opening release\b", "Shunt release (SHT)"),
        (r"\bexcitation release\b", "Shunt release (SHT)"),
        (r"\bshunt trip\b", "Shunt release (SHT)"),
        (r"\black voltage\b", "Undervoltage release (UVT)"),
        (r"\bten thousand times\b", "plain integer operating cycles"),
        (r"\binstallation and debugging\b", "installation and commissioning"),
        (r"\bmatters need attention\b", "operating precautions"),
        (r"\bordering instructions?\b", "ordering information"),
        (r"\bwrong action\b", "false tripping"),
        (r"\berror work\b", "false tripping"),
        (r"\bno tolerance specified\b", "unspecified linear tolerance"),
        (r"\buse class(?:es)?\b", "selectivity category / utilization category"),
        (r"\bdrawer(?:\s+(?:type|box|seat|cradle|base))?\b", "Withdrawable / Withdrawable cradle (IEC Cl. 3.5)"),
    ],
    "BLACKLIST_ACB": [
        (r"\bclosed electromagnet\b", "Closing release (CEM)"),
        (r"\bclose electromagnet\b", "Closing release (CEM)"),
        (r"\bclosing electromagnet\b", "Closing release (CEM)"),
        (r"\bclosing magnet\b", "Closing release (CEM)"),
        (r"\bearch current transformer\b", "Earth current transformer (ECT)"),
        (r"\binterphased\b", "interphase barrier (DD / FD)"),
        (r"\binter phased\b", "interphase barrier (DD / FD)"),
        (r"\bphase space plate\b", "interphase barrier (DD / FD)"),
        (r"\bunder voltage delay release-zero\b", "Loss-of-voltage time-delay release (UVTZ)"),
        (r"\bclosing preparation contact\b", "Ready-to-close contact (SPC)"),
        (r"\bseparation position\b", "Disconnected position (Cl. 8.1.2)"),
        (r"\bconnection position\b", "Connected position"),
        (r"\bhole opener\b", "panel hole saw"),
        (r"\bface mask\b", "Door escutcheon"),
        (r"\bstorage hole\b", "Racking handle storage slot"),
        (r"\bbody key lock\b", "Key lock (KL)"),
        (r"\brefuses to open\b", "does not trip / cannot be opened"),
        (r"\bis forbidden to open\b", "cannot be opened"),
        (r"\birrelevant to\b", "independent of"),
        (r"\bpulse energization working mode\b", "pulse-energization duty"),
        (r"\buniversal circuit[- ]breaker\b", "Air circuit-breaker (ACB)"),
        (r"\bintelligent air circuit[- ]breaker\b", "Air circuit-breaker with electronic trip unit"),
        (r"\blvpcb\b", "Air circuit-breaker (ACB)"),
    ],
    "BLACKLIST_MCCB": [
        (r"\bplastic shell breaker\b", "Moulded-case circuit-breaker (MCCB)"),
        (r"\bplastic case breaker\b", "Moulded-case circuit-breaker (MCCB)"),
        (r"\bleakage plastic shell\b", "Circuit-breaker incorporating residual current protection (CBR)"),
        (r"\bearth leakage breaker\b", "Circuit-breaker incorporating residual current protection (CBR)"),
        (r"\belcb\b", "Circuit-breaker incorporating residual current protection (CBR)"),
        (r"\bmotor circuit protector\b", "Instantaneous trip circuit-breaker (ICB) (Annex O)"),
        (r"\bnon-automatic breaker\b", "CBI (Annex L) / switch-disconnector (IEC 60947-3)"),
        (r"\bdouble breaking point\b", "Rotary double-break contact system"),
        (r"\bback wiring\b", "Rear connection (HR / VR)"),
        (r"\binsert installation\b", "Plug-in base"),
        (r"\brotate handle\b", "Rotary handle"),
        (r"\bwire cover\b", "Terminal shield"),
        (r"\bmotor hand\b", "Motor-operator (MOD)"),
        (r"\bclosing magnet\b", "Closing release"),
    ],
    "COMPETITOR_RULES_COMMON": [
        (r"(?<![A-Za-z0-9\-])MX(?![A-Za-z0-9\-])", "SHT (Shunt release)"),
        (r"(?<![A-Za-z0-9\-])MN(?![A-Za-z0-9\-])", "UVT (Undervoltage release)"),
        (r"(?<![A-Za-z0-9\-])SDE(?![A-Za-z0-9\-])", "AL (Alarm switch)"),
        (r"\(OF\)", "(AX) (Auxiliary contact)"),
        (r"\(YO\)", "(SHT) (Shunt release)"),
    ],
    "COMPETITOR_RULES_ACB": [
        (r"(?<![A-Za-z0-9\-])XF(?![A-Za-z0-9\-])", "CEM (Closing release)"),
        (r"\(PF\)|\bPF\s+contact\b", "SPC (Ready-to-close contact)"),
        (r"(?<![A-Za-z0-9\-])MCH(?![A-Za-z0-9\-])", "MOD (Motor-operator)"),
        (r"(?<![A-Za-z0-9\-])KLC(?![A-Za-z0-9\-])", "KL (Key lock)"),
    ],
    "STD_CONCEPT_ZH": [
        (r"相间对中性线", "相-中性线 (IEC 60947-2:2024 Cl. 5.3.6.2.3)"),
        (r"(?<![单两二三四多])极极限", "单极极限"),
        (r"隔离开关断路器", "隔离开关 (IEC 60947-3 / GB/T 14048.3)"),
        (r"使用类别\s*[AB](?![A-Za-z0-9\-])", "选择性类别 A / B (GB/T 14048.2—2020 Cl. 3.1 / 4.4)"),
        (r"抽出式断路器", "抽屉式断路器 (GB/T 14048.2—2020 Cl. 2.5 / 3.7)"),
        (r"结构差异", "结构段 (GB/T 14048.2—2020 Cl. 2.1.2 / 7.1.6)"),
        (r"合闸涌流脱扣器", "接通电流脱扣器 (GB/T 14048.2—2020 Cl. 2.10)"),
    ],
    "STD_STATUTORY_ZH": [
        (r"闭合电磁铁|合闸电磁铁|释能电磁铁", "闭合脱扣器 (GB/T 14048.2—2020 Cl. 2.23)"),
        (r"万能式断路器", "空气断路器（分类：万能式） (GB/T 14048.2—2020 Cl. 2.7 / 3.3)"),
        (r"(?<!塑料外壳式)塑壳断路器", "塑料外壳式断路器 (GB/T 14048.2—2020 Cl. 2.6 / 3.3)"),
        (r"功率损耗", "功耗 (GB/T 14048.2—2020 附录 G)"),
        (r"(?<![\"“])分离位置|“分离”\s*位置", "隔离位置 (GB/T 14048.2—2020 Cl. 7.1.2；Cl. 2.5 称抽出位置)"),
        (r"\bInm\b", "壳架等级（GB/T 14048.2—2020 Cl. 2.1.1 / IEC 3.1.1 未定义 Inm 符号）"),
        (r"漏电保护", "剩余电流保护 (GB/T 14048.2—2020 附录 B/R)"),
        (r"漏电互感器", "电流传感器（GB/T 14048.2—2020 附录 B/M；产品扩展可用「剩余电流互感器」）"),
    ],
    "ED5_CLAUSE_RE": re.compile(
        r"(?:Cl\.|Clause)\s*(?:2\.(?:[1-9]|1\d|2[0-3])(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|4\.[6-8](?:\.\d+)?|7\.[12](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?|8\.[45](?:\.\d+)?)\b",
        re.IGNORECASE,
    ),
    "ED5_GUARD_TAGS": ("60947-1", "60947-3", "14048.2", "GB/T", "GB ", "60947-2:2024", "60947-2:20"),
}


def load_translation_ssot(translation_dir: Path | None) -> tuple[dict, str, str | None]:
    if translation_dir is not None:
        lint_path = translation_dir / "scripts" / "lint_text.py"
        if lint_path.is_file():
            spec = importlib.util.spec_from_file_location("_chint_translation_ssot", str(lint_path))
            if spec is not None and spec.loader is not None:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                ssot = {
                    "BLACKLIST_COMMON": list(getattr(mod, "BLACKLIST_COMMON", [])),
                    "BLACKLIST_ACB": list(getattr(mod, "BLACKLIST_ACB", [])),
                    "BLACKLIST_MCCB": list(getattr(mod, "BLACKLIST_MCCB", [])),
                    "COMPETITOR_RULES_COMMON": list(getattr(mod, "COMPETITOR_RULES_COMMON", [])),
                    "COMPETITOR_RULES_ACB": list(getattr(mod, "COMPETITOR_RULES_ACB", [])),
                    "STD_CONCEPT_ZH": list(getattr(mod, "STD_CONCEPT_ZH", [])),
                    "STD_STATUTORY_ZH": list(getattr(mod, "STD_STATUTORY_ZH", [])),
                    "ED5_CLAUSE_RE": getattr(mod, "ED5_CLAUSE_RE", None),
                    "ED5_GUARD_TAGS": tuple(getattr(mod, "ED5_GUARD_TAGS", ())),
                }
                return ssot, "sibling:chint-translation", str(translation_dir)
    return dict(BUILTIN_SSOT_FALLBACK), "builtin-standalone", None


# ---------------------------------------------------------------------------
# Office Extraction & PDF Annotation (Sibling-First + Built-in Standalone)
# ---------------------------------------------------------------------------

def _import_fitz():
    try:
        import fitz
        return fitz
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'pymupdf' (fitz) required for .pdf processing. "
            "Install with: python3 -m pip install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ) from exc


def _import_openpyxl():
    try:
        import openpyxl
        return openpyxl
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'openpyxl' required for .xlsx processing. "
            "Install with: python3 -m pip install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ) from exc


def parse_page_spec(spec: str | None) -> set[int] | None:
    if spec is None:
        return None
    cleaned = spec.strip()
    if not cleaned:
        raise ValueError("Empty --pages specification; provide e.g. '1-20' or '1,3,5'.")
    pages: set[int] = set()
    for part in cleaned.split(","):
        part = part.strip()
        if not part:
            raise ValueError(f"Invalid empty segment in --pages '{spec}'.")
        if "-" in part:
            m = re.fullmatch(r"(\d+)-(\d+)", part)
            if not m:
                raise ValueError(f"Invalid page range '{part}' in --pages '{spec}'; expected positive integers like '1-20'.")
            lo, hi = int(m.group(1)), int(m.group(2))
            if lo < 1 or hi < lo:
                raise ValueError(f"Invalid page range '{part}' in --pages '{spec}'; start must be >= 1 and <= end.")
            pages.update(range(lo, hi + 1))
        else:
            if not re.fullmatch(r"\d+", part) or int(part) < 1:
                raise ValueError(f"Invalid page number '{part}' in --pages '{spec}'; expected integer >= 1.")
            pages.add(int(part))
    if not pages:
        raise ValueError(f"Empty page selection from --pages '{spec}'.")
    return pages


def _docx_xml_sort_key(name: str) -> tuple[int, int, str]:
    stem = Path(name).stem
    if stem.startswith("header"):
        return (0, int(re.sub(r"\D+", "", stem) or 0), stem)
    if stem == "document":
        return (1, 0, stem)
    if stem == "footnotes":
        return (2, 0, stem)
    if stem == "endnotes":
        return (3, 0, stem)
    if stem == "comments":
        return (4, 0, stem)
    if stem.startswith("footer"):
        return (5, int(re.sub(r"\D+", "", stem) or 0), stem)
    return (6, 0, stem)


def _docx_para_text(elem: ET.Element, ns: str) -> str:
    parts: list[str] = []

    def _walk(node: ET.Element) -> None:
        tag = node.tag
        if tag == f"{ns}txbxContent":
            return
        if tag == f"{ns}t":
            if node.text:
                parts.append(node.text)
            return
        if tag == f"{ns}tab":
            parts.append("\t")
            return
        if tag in (f"{ns}br", f"{ns}cr"):
            parts.append("\n")
            return
        for child in node:
            _walk(child)

    for child in elem:
        _walk(child)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Legacy OLE2 (Compound File Binary) — pure stdlib, .doc / .xls only
# ---------------------------------------------------------------------------

_OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_OLE2_END = 0xFFFFFFFE

# Word control characters: table-cell/end-of-cell -> tab, soft break -> newline,
# field/object anchors dropped. Anything else unprintable is filtered later.
_WORD_CTRL_TRANS = {
    0x01: "", 0x02: "", 0x05: "", 0x07: "\t", 0x08: "", 0x0B: "\n",
    0x13: "", 0x14: "", 0x15: "", 0x1E: "-", 0x1F: "", 0xA0: " ",
}


def _u16(buf: bytes, off: int) -> int:
    return int.from_bytes(buf[off:off + 2], "little")


def _u32(buf: bytes, off: int) -> int:
    return int.from_bytes(buf[off:off + 4], "little")


def _ole2_streams(data: bytes) -> dict[str, bytes]:
    """Parse an OLE2/CFB container into {stream name: bytes}.

    Covers only what Word 97 and BIFF8 need: header, DIFAT/FAT, MiniFAT, directory.
    ponytail: no property-set/encryption handling; a corrupt chain raises instead of
    guessing, which is the required behaviour for an audit tool (silent empty text
    would surface as a fake "0 findings" pass).
    """
    if len(data) < 512 or data[:8] != _OLE2_MAGIC:
        raise ValueError("文件头魔数不符，不是 OLE2 复合文档或文件已损坏")
    ssz = 1 << _u16(data, 30)
    mssz = 1 << _u16(data, 32)
    if ssz not in (512, 4096) or mssz <= 0 or mssz > ssz:
        raise ValueError(f"扇区大小异常（sector={ssz}, mini={mssz}）")
    n_fat = _u32(data, 0x2C)
    dir_start = _u32(data, 0x30)
    cutoff = _u32(data, 0x38) or 4096
    minifat_start = _u32(data, 0x3C)
    difat_start = _u32(data, 0x44)

    def sector(idx: int) -> bytes:
        off = (idx + 1) * ssz
        if idx >= _OLE2_END or off + ssz > len(data):
            raise ValueError(f"扇区 {idx} 越界（文件被截断）")
        return data[off:off + ssz]

    difat = [_u32(data, 0x4C + 4 * i) for i in range(109)]
    nxt, guard = difat_start, 0
    while nxt < _OLE2_END:
        blk = sector(nxt)
        difat.extend(_u32(blk, 4 * i) for i in range(ssz // 4 - 1))
        nxt = _u32(blk, ssz - 4)
        guard += 1
        if guard > len(data) // ssz + 1:
            raise ValueError("DIFAT 链存在循环")

    fat: list[int] = []
    for fs in [s for s in difat if s < _OLE2_END][:n_fat]:
        blk = sector(fs)
        fat.extend(_u32(blk, 4 * i) for i in range(ssz // 4))
    if not fat:
        raise ValueError("FAT 为空")

    def chain(start: int, table: list[int]) -> list[int]:
        out: list[int] = []
        cur = start
        while cur < _OLE2_END:
            if cur >= len(table) or cur in out:
                raise ValueError("扇区链越界或存在循环")
            out.append(cur)
            cur = table[cur]
            if len(out) > len(table):
                raise ValueError("扇区链存在循环")
        return out

    def read_fat(start: int, size: int | None) -> bytes:
        buf = bytearray()
        for s in chain(start, fat):
            buf.extend(sector(s))
        return bytes(buf[:size] if size is not None else buf)

    dirdata = read_fat(dir_start, None)
    entries: list[tuple[str, int, int, int]] = []
    for i in range(len(dirdata) // 128):
        e = dirdata[i * 128:(i + 1) * 128]
        nlen = _u16(e, 64)
        name = e[:max(0, nlen - 2)].decode("utf-16le") if 2 <= nlen <= 64 else ""
        entries.append((name, e[66], _u32(e, 116), _u32(e, 120)))
    if not entries or entries[0][1] != 5:
        raise ValueError("目录项缺少根条目")
    _, _, root_start, root_size = entries[0]

    mini_stream = read_fat(root_start, root_size) if root_start < _OLE2_END and root_size else b""
    mini_fat: list[int] = []
    if minifat_start < _OLE2_END:
        mf = read_fat(minifat_start, None)
        mini_fat = [_u32(mf, 4 * i) for i in range(len(mf) // 4)]

    def read_mini(start: int, size: int) -> bytes:
        buf = bytearray()
        cur = start
        seen: set[int] = set()
        while cur < _OLE2_END and cur < len(mini_fat) and cur not in seen:
            seen.add(cur)
            off = cur * mssz
            buf.extend(mini_stream[off:off + mssz])
            cur = mini_fat[cur]
            if len(buf) >= size:
                break
        return bytes(buf[:size])

    streams: dict[str, bytes] = {}
    for name, etype, start, size in entries:
        if etype != 2 or size == 0:
            continue
        streams[name] = read_mini(start, size) if size < cutoff else read_fat(start, size)
    return streams


def _decode_legacy_bytes(raw: bytes) -> str:
    """Decode a 1-byte Word/BIFF piece without errors="replace".

    ponytail: heuristic — ASCII fast path, then GB18030 (this skill's corpus is Chinese),
    then cp1252. A Western doc whose accented bytes form a valid GB18030 pair may lose a
    character; upgrade to per-language code-page selection only if that shows up.
    """
    if all(b < 0x80 for b in raw):
        return raw.decode("ascii")
    for enc in ("gb18030", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("单字节文本片段既非 GB18030 也非 cp1252 编码")


def _doc_piece_text(wd: bytes, clx: bytes) -> str:
    """Word 97+ text from the CLX piece table (compressed and UTF-16LE pieces)."""
    if not clx:
        raise ValueError("CLX 为空")
    plc = None
    i = 0
    while i < len(clx):
        kind = clx[i]
        if kind == 0x01:
            if i + 3 > len(clx):
                raise ValueError("CLX Prc 记录截断")
            i += 3 + _u16(clx, i + 1)
        elif kind == 0x02:
            if i + 5 > len(clx):
                raise ValueError("CLX Pcdt 记录截断")
            lcb = _u32(clx, i + 1)
            plc = clx[i + 5:i + 5 + lcb]
            break
        else:
            raise ValueError(f"CLX 未知记录类型 0x{kind:02x}")
    if plc is None or len(plc) < 16:
        raise ValueError("CLX 缺少片段表（Pcdt）")
    n = (len(plc) - 4) // 12
    cps = [_u32(plc, 4 * k) for k in range(n + 1)]
    base = 4 * (n + 1)
    parts: list[str] = []
    for k in range(n):
        cch = cps[k + 1] - cps[k]
        if cch <= 0:
            continue
        fc_raw = _u32(plc, base + 8 * k + 2)
        compressed = bool(fc_raw & 0x40000000)
        fc = fc_raw & 0x3FFFFFFF
        if compressed:
            fc //= 2
            raw = wd[fc:fc + cch]
            if len(raw) != cch:
                raise ValueError("文本片段越界")
            parts.append(_decode_legacy_bytes(raw))
        else:
            raw = wd[fc:fc + 2 * cch]
            if len(raw) != 2 * cch:
                raise ValueError("文本片段越界")
            parts.append(raw.decode("utf-16le"))
    return "".join(parts)


def _doc_raw_scan(raw: bytes, ccp_text: int) -> str:
    """Fallback when the CLX is unreadable: pick the most plausible decode of the raw run.

    Word 6/95 stores 1-byte text; Word 97+ stores UTF-16LE. Neither the FIB nor the
    stream header can be trusted once the piece table failed, so both are scored and
    the winner is filtered to printable runs by the caller.
    """
    if not raw:
        return ""
    cands: list[str] = []
    even = raw[:2 * ccp_text] if ccp_text and 2 * ccp_text <= len(raw) else raw[:len(raw) & ~1]
    try:
        cands.append(even.decode("utf-16le"))
    except UnicodeDecodeError:
        pass
    for enc in ("gb18030", "cp1252"):
        try:
            cands.append(raw[:ccp_text or len(raw)].decode(enc))
        except UnicodeDecodeError:
            continue
    if not cands:
        raise ValueError("正文既非 UTF-16LE 也非 GB18030/cp1252 编码")

    def score(t: str) -> float:
        if not t:
            return 0.0
        printable = sum(1 for ch in t if ch.isprintable() or ch in "\r\n\t")
        cjk = sum(1 for ch in t if "一" <= ch <= "鿿")
        return printable / len(t) + cjk / len(t) * 0.5

    return max(cands, key=score)


def _extract_doc_units(streams: dict[str, bytes]) -> list[str]:
    """Word 97/.doc body text, one string per paragraph."""
    wd = streams.get("WordDocument")
    if not wd or len(wd) < 0x200:
        raise ValueError("缺少 WordDocument 流")
    if _u16(wd, 0) != 0xA5EC:
        raise ValueError("WordDocument 流标识 wIdent 不符")
    ccp_text = _u32(wd, 0x4C)
    fc_min = _u32(wd, 0x18)
    n_fib = _u16(wd, 2)

    text = ""
    if n_fib >= 0xC1 and ccp_text:
        table = streams.get("1Table" if _u16(wd, 0x0A) & 0x0200 else "0Table")
        fc_clx, lcb_clx = _u32(wd, 0x01A2), _u32(wd, 0x01A6)
        if table and lcb_clx and fc_clx + lcb_clx <= len(table):
            try:
                text = _doc_piece_text(wd, table[fc_clx:fc_clx + lcb_clx])[:ccp_text]
            except (ValueError, IndexError, struct.error):
                text = ""
    if not text.strip():
        if ccp_text == 0:
            return []  # genuinely empty document, not a blind pass
        text = _doc_raw_scan(wd[fc_min:], ccp_text)

    cleaned = "".join(
        ch for ch in text.translate(_WORD_CTRL_TRANS)
        if ch in "\t\n\r" or ch.isprintable()
    )
    paras: list[str] = []
    for block in cleaned.split("\r"):
        for line in block.split("\n"):
            if line.strip():
                paras.append(line.strip())
    if not paras:
        raise ValueError("文件结构可解析但未提取到正文（可能是图片型文档或加密文档）")
    return paras


def _biff_records(data: bytes):
    pos = 0
    while pos + 4 <= len(data):
        rid = _u16(data, pos)
        ln = _u16(data, pos + 2)
        if pos + 4 + ln > len(data):
            raise ValueError(f"BIFF 记录 0x{rid:04X} 在偏移 {pos} 处超出流长度")
        yield pos, rid, data[pos + 4:pos + 4 + ln]
        pos += 4 + ln


def _biff_sst(chunks: list[bytes]) -> list[str]:
    """Shared-string table across SST + CONTINUE records (MS-XLS 2.4.271).

    A CONTINUE that splits a string's character data starts with a fresh 1-byte
    fHighByte flag; splits inside rich-text runs / ExtRst carry no flag. A string
    header is never split, so header reads may skip to the next chunk freely.
    """
    if not chunks or len(chunks[0]) < 8:
        raise ValueError("SST 记录截断")
    unique = _u32(chunks[0], 4)
    ci, p = 0, 8
    out: list[str] = []

    def advance() -> None:
        nonlocal ci, p
        ci += 1
        if ci >= len(chunks):
            raise ValueError("SST 字符串数量与 CONTINUE 记录不符")
        p = 0

    def take(n: int) -> bytes:
        """Read n bytes, crossing chunk boundaries WITHOUT consuming a flag byte."""
        nonlocal ci, p
        buf = bytearray()
        while n > 0:
            if ci >= len(chunks):
                raise ValueError("SST 记录截断")
            avail = len(chunks[ci]) - p
            if avail <= 0:
                advance()
                continue
            k = min(n, avail)
            buf.extend(chunks[ci][p:p + k])
            p += k
            n -= k
        return bytes(buf)

    while len(out) < unique:
        while ci < len(chunks) and len(chunks[ci]) - p < 3:
            advance()
        hdr = take(3)
        cch = _u16(hdr, 0)
        flags = hdr[2]
        compressed = not (flags & 0x01)
        nrun = _u16(take(2), 0) if flags & 0x08 else 0
        cbext = _u32(take(4), 0) if flags & 0x04 else 0
        remaining = cch
        parts: list[str] = []
        while remaining:
            if ci >= len(chunks):
                raise ValueError("SST 字符串字符数据截断")
            if p >= len(chunks[ci]):
                advance()
                if p < len(chunks[ci]):
                    compressed = not (chunks[ci][p] & 0x01)
                    p += 1
                continue
            avail = len(chunks[ci]) - p
            if compressed:
                k = min(remaining, avail)
                parts.append(chunks[ci][p:p + k].decode("latin-1"))
                p += k
            else:
                k = min(remaining, avail // 2)
                parts.append(chunks[ci][p:p + 2 * k].decode("utf-16le"))
                p += 2 * k
                if k == 0:
                    raise ValueError("SST UTF-16 片段在 CONTINUE 边界出现奇数字节")
            remaining -= k
        if nrun or cbext:
            take(nrun * 4 + cbext)
        out.append("".join(parts))
    return out


def _xls_rk(value: int) -> float:
    if value & 0x02:
        n = value >> 2
        if n & 0x20000000:
            n -= 0x40000000
        out = float(n)
    else:
        out = struct.unpack("<d", b"\x00\x00\x00\x00" + struct.pack("<I", value & 0xFFFFFFFC))[0]
    if value & 0x01:
        out /= 100.0
    return out


def _fmt_num(v: float) -> str:
    if v != v or v in (float("inf"), float("-inf")):
        return ""  # NaN/Inf are error-result placeholders, not text
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:.10g}"


def _xl_unicode_string(payload: bytes, off: int) -> str:
    if off + 3 > len(payload):
        raise ValueError("BIFF 字符串截断")
    cch = _u16(payload, off)
    flags = payload[off + 2]
    pos = off + 3
    if flags & 0x08:
        pos += 2 + 4 * _u16(payload, pos)
    if flags & 0x04:
        pos += 4
    if flags & 0x01:
        return payload[pos:pos + 2 * cch].decode("utf-16le")
    return _decode_legacy_bytes(payload[pos:pos + cch])


def _extract_xls_units(streams: dict[str, bytes]) -> list[dict]:
    """BIFF8 cell text, one unit per non-empty row: `X<sheet>:R<row>` (row is 1-based)."""
    wb = streams.get("Workbook") or streams.get("Book")
    if not wb:
        raise ValueError("缺少 Workbook/Book 流")
    recs = list(_biff_records(wb))
    if not recs:
        raise ValueError("未找到任何 BIFF 记录")

    version = _u16(recs[0][2], 0) if recs[0][1] == 0x0809 and len(recs[0][2]) >= 2 else None
    if version == 0x0500:
        raise ValueError("BIFF5（Excel 95）格式不受支持，请用 Excel 另存为 .xlsx 后重试")
    if version != 0x0600:
        raise ValueError(f"Workbook 流版本未知（BOF 版本 0x{version:04X}）" if version else "Workbook 流缺少 BOF 记录")

    sheet_at: dict[int, str] = {}
    sheet_order: list[str] = []
    rows: dict[str, dict[int, dict[int, str]]] = {}
    sst: list[str] = []
    cur: str | None = None
    pending: tuple[str, int, int] | None = None

    def put(sheet: str, row: int, col: int, text: str) -> None:
        if text:
            rows.setdefault(sheet, {}).setdefault(row, {})[col] = text

    i = 0
    while i < len(recs):
        pos, rid, payload = recs[i]
        if pos in sheet_at:
            cur = sheet_at[pos]
        if rid == 0x0085:
            if len(payload) >= 8:
                lb = _u32(payload, 0)
                if payload[5] == 0:  # dt at offset 5: 0 = worksheet (2=chart, 6=VB module)
                    cch, flags = payload[6], payload[7]
                    name = (
                        payload[8:8 + 2 * cch].decode("utf-16le")
                        if flags & 0x01 else _decode_legacy_bytes(payload[8:8 + cch])
                    )
                    sheet_at[lb] = name
                    if name not in sheet_order:
                        sheet_order.append(name)
        elif rid == 0x00FC:
            chunks = [payload]
            j = i + 1
            while j < len(recs) and recs[j][1] == 0x003C:
                chunks.append(recs[j][2])
                j += 1
            sst = _biff_sst(chunks)
            i = j
            continue
        elif cur is None:
            pass  # workbook globals: no cell data
        elif rid == 0x00FD and len(payload) >= 10:  # LABELSST
            isst = _u32(payload, 6)
            if isst >= len(sst):
                raise ValueError(f"LABELSST 引用了不存在的共享字符串索引 {isst}（SST 共 {len(sst)} 条）")
            put(cur, _u16(payload, 0), _u16(payload, 2), sst[isst])
        elif rid in (0x0204, 0x00D6) and len(payload) >= 6:  # LABEL / RSTRING
            put(cur, _u16(payload, 0), _u16(payload, 2), _xl_unicode_string(payload, 6))
        elif rid == 0x0203 and len(payload) >= 14:  # NUMBER
            put(cur, _u16(payload, 0), _u16(payload, 2),
                _fmt_num(struct.unpack("<d", payload[6:14])[0]))
        elif rid == 0x027E and len(payload) >= 10:  # RK
            put(cur, _u16(payload, 0), _u16(payload, 2), _fmt_num(_xls_rk(_u32(payload, 6))))
        elif rid == 0x00BD and len(payload) >= 12:  # MULRK
            row, col = _u16(payload, 0), _u16(payload, 2)
            for k in range((len(payload) - 6) // 6):
                off = 4 + 6 * k
                put(cur, row, col + k, _fmt_num(_xls_rk(_u32(payload, off + 2))))
        elif rid == 0x0205 and len(payload) >= 8:  # BOOLERR
            if not payload[7]:
                put(cur, _u16(payload, 0), _u16(payload, 2), "TRUE" if payload[6] else "FALSE")
        elif rid == 0x0006 and len(payload) >= 14:  # FORMULA: cached result only
            row, col = _u16(payload, 0), _u16(payload, 2)
            if payload[6:8] == b"\xff\xff":
                kind = payload[8]
                if kind == 1:
                    put(cur, row, col, "TRUE" if payload[9] else "FALSE")
                elif kind == 2:
                    pass  # cached error, not text
                elif kind == 0:
                    pending = (cur, row, col)  # string result arrives in the STRING record
            else:
                put(cur, row, col, _fmt_num(struct.unpack("<d", payload[6:14])[0]))
        elif rid == 0x0207 and cur is not None and len(payload) >= 3:  # STRING
            if pending is not None:
                put(pending[0], pending[1], pending[2], _xl_unicode_string(payload, 0))
            pending = None
        i += 1

    if not sheet_order:
        raise ValueError("未找到任何工作表（BOUNDSHEET 记录缺失）")

    units: list[dict] = []
    for sheet in sheet_order:
        for r in sorted(rows.get(sheet, {})):
            cells = rows[sheet][r]
            joined = " | ".join(cells[c].strip() for c in sorted(cells) if cells[c].strip())
            if joined:
                units.append({"location": f"X{sheet}:R{r + 1}", "text": joined})
    if not units:
        raise ValueError("文件结构可解析但未提取到任何单元格文本（工作表可能为空或含不支持的加密内容）")
    return units


# ---------------------------------------------------------------------------
# Modern OOXML (.pptx) and Markdown — pure stdlib
# ---------------------------------------------------------------------------

_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _pptx_para_text(para: ET.Element) -> str:
    """Paragraph text: `a:t` runs concatenated, `a:br` as a newline, `a:tab` as a tab.

    ElementTree already unescapes XML entities; a manual `&amp;` replace would double-decode.
    """
    parts: list[str] = []
    for node in para.iter():
        if node.tag == f"{{{_A_NS}}}t":
            if node.text:
                parts.append(node.text)
        elif node.tag == f"{{{_A_NS}}}br":
            parts.append("\n")
        elif node.tag == f"{{{_A_NS}}}tab":
            parts.append("\t")
    return "".join(parts)


def _pptx_shapes(node: ET.Element):
    """Text-bearing shapes (`p:sp`, `p:graphicFrame`) in document order.

    Walks every element rather than only direct children, so text inside `<p:grpSp>`
    group shapes is reached without a hand-written recursion that can miscount.
    """
    for child in node.iter():
        if child.tag in (f"{{{_P_NS}}}sp", f"{{{_P_NS}}}graphicFrame"):
            yield child


def _extract_pptx_units(p: Path) -> tuple[list[dict], list[int], int]:
    """Slides in numeric order (slide2 before slide10), one unit per non-empty paragraph.

    Location `S<slide>:T<shape>:P<para>`. `_PAGE_LOC_RE` matches only `P<n>:`, so these
    stay document-scoped: cross-line detectors group the whole deck into one `__all__`
    block exactly as they do for docx paragraphs. Slides yielding no text are returned
    separately so the blind-pass guard can fire on an image-only deck.
    """
    try:
        zf = zipfile.ZipFile(str(p))
    except zipfile.BadZipFile as exc:
        raise ValueError(f"无法解析 .pptx（不是有效的 OOXML 压缩包：{exc}），建议用 PowerPoint 另存后重试") from exc
    units: list[dict] = []
    low_slides: list[int] = []
    with zf:
        slides = []
        for name in zf.namelist():
            m = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
            if m:
                slides.append((int(m.group(1)), name))
        if not slides:
            raise ValueError("无法解析 .pptx（压缩包内没有 ppt/slides/slideN.xml）")
        slides.sort(key=lambda x: x[0])
        for snum, name in slides:
            try:
                root = ET.fromstring(zf.read(name))
            except ET.ParseError as exc:
                raise ValueError(f"无法解析幻灯片 {snum}（XML 损坏：{exc}）") from exc
            produced = 0
            for t_idx, shape in enumerate(_pptx_shapes(root), 1):
                for p_idx, para in enumerate(shape.iter(f"{{{_A_NS}}}p"), 1):
                    txt = _pptx_para_text(para).strip()
                    if txt:
                        units.append({"location": f"S{snum}:T{t_idx}:P{p_idx}", "text": txt})
                        produced += 1
            if produced == 0:
                low_slides.append(snum)
    return units, low_slides, len(slides)


_MD_FENCE_RE = re.compile(r"^\s{0,3}(?:```+|~~~+)")
_MD_INLINE_CODE_RE = re.compile(r"`+[^`]*`+")


def _extract_md_units(text: str) -> list[dict]:
    """Markdown prose only: fenced blocks and inline-code spans are not audited as prose.

    Locator is `M<line>` (1-based source line; `.txt` keeps `Line <n>`). Headings are
    not parsed — locators stay traceable to the raw file. A file that is entirely
    fenced yields zero units, which is a legitimate empty result, not a blind pass.
    """
    units: list[dict] = []
    in_fence = False
    for lno, line in enumerate(text.splitlines(), 1):
        if _MD_FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        prose = _MD_INLINE_CODE_RE.sub(" ", line)
        if prose.strip():
            units.append({"location": f"M{lno}", "text": prose})
    return units


_ELECTRICAL_SIGNAL_RE = re.compile(
    r"\b(?:Icu|Ics|Inm|Icw|Ue|Ui|Uimp)\b|额定|壳架|分断|断路器", re.IGNORECASE
)


def classify_doc_type(units: list[tuple[str, str]], ext: str) -> str:
    """`catalogue` | `office-generic` | `markdown` | `legacy-binary` | `text`.

    Catalogue vs generic is decided by content, not filename: at least two distinct
    electrical signals in the first 400 units. A generic deck that merely says
    "断路器" once stays `office-generic`, so its report is read with the right noise
    expectation.
    """
    if ext in {".doc", ".xls"}:
        return "legacy-binary"
    if ext == ".md":
        return "markdown"
    if ext in {".txt", ""}:
        return "text"
    blob = " ".join(t for _, t in units[:400])
    signals = {m.group(0).lower() for m in _ELECTRICAL_SIGNAL_RE.finditer(blob)}
    return "catalogue" if len(signals) >= 2 else "office-generic"


def _check_not_lfs_pointer(p: Path) -> None:
    if p.is_file() and p.stat().st_size < 512:
        try:
            head = p.read_bytes()[:64]
        except OSError:
            return
        if head.startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(
                f"文件 '{p.name}' 是未还原的 Git LFS 指针，请先执行 git lfs pull / git lfs checkout 还原真实文件后再审校。"
            )


def _extract_office_builtin(source: str, pages_filter: set[int] | None = None) -> dict:
    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {source}")
    _check_not_lfs_pointer(p)
    ext = p.suffix.lower()
    if ext in {".doc", ".xls"}:
        try:
            streams = _ole2_streams(p.read_bytes())
            if ext == ".doc":
                paras = _extract_doc_units(streams)
                units = [{"location": f"D{i}", "text": t} for i, t in enumerate(paras, 1)]
                total = len(units)
            else:
                units = _extract_xls_units(streams)
                total = len(units)
        except (ValueError, IndexError, KeyError, struct.error) as exc:
            target = "docx" if ext == ".doc" else "xlsx"
            raise ValueError(
                f"无法解析 {ext}（OLE2 结构异常：{exc}），建议用 Office 另存为 .{target} 后重试"
            ) from exc
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": ext.lstrip("."),
            "total_units": total,
            "scanned_units": total,
            "low_text_pages": [],
            "uncached_formula_cells": [],
            "units": units,
            "doc_type": "legacy-binary",
        }

    if ext == ".pptx":
        units, low_slides, slide_count = _extract_pptx_units(p)
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": "pptx",
            "total_units": slide_count,
            "scanned_units": slide_count,
            "low_text_pages": low_slides,
            "uncached_formula_cells": [],
            "units": units,
            "doc_type": classify_doc_type([(u["location"], u["text"]) for u in units], ext),
        }

    if ext == ".md":
        units = _extract_md_units(_read_text_any(p))
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": "md",
            "total_units": len(units),
            "scanned_units": len(units),
            "low_text_pages": [],
            "uncached_formula_cells": [],
            "units": units,
            "doc_type": "markdown",
        }

    if ext == ".pdf":
        fitz = _import_fitz()
        try:
            doc = fitz.open(str(p))
        except Exception as exc:
            raise RuntimeError(f"Failed to open PDF '{source}': {exc}") from exc
        try:
            if doc.is_encrypted:
                raise ValueError(f"PDF '{source}' is encrypted/password-protected; decrypt before extraction.")
            total, scanned = len(doc), 0
            tables: list[dict] = []

            def pages_filter_ok(pno: int) -> bool:
                return pages_filter is None or pno in pages_filter

            if pages_filter is not None:
                invalid = sorted(n for n in pages_filter if n > total)
                if invalid:
                    raise ValueError(f"--pages exceeds PDF page count ({total}): {invalid[:5]}")
            units, low_pages = [], []
            for idx, page in enumerate(doc, 1):
                if pages_filter is not None and idx not in pages_filter:
                    continue
                scanned += 1
                txt = page.get_text("text")
                if len(re.sub(r"\s+", "", txt)) < LOW_TEXT_THRESHOLD:
                    low_pages.append(idx)
                for lno, line in enumerate(txt.splitlines(), 1):
                    if line.strip():
                        units.append({"location": f"P{idx}:L{lno}", "text": line})
                if TABLE_KW_RE.search(txt) and pages_filter_ok(idx):
                    tables.extend(_extract_page_tables(page, idx))
            return {
                "schema": "chint-office-extract/v1",
                "source": str(p),
                "format": "pdf",
                "total_units": total,
                "scanned_units": scanned,
                "low_text_pages": low_pages,
                "uncached_formula_cells": [],
                "units": units,
                "tables": tables,
                "doc_type": classify_doc_type(
                    [(u["location"], u["text"]) for u in units], ext
                ),
            }
        finally:
            doc.close()

    if ext == ".docx":
        units = []
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(str(p)) as zf:
            xml_names = [
                n for n in zf.namelist()
                if re.match(r"word/(header\d+|document|footnotes|endnotes|comments|footer\d+)\.xml$", n)
            ]
            for name in sorted(xml_names, key=_docx_xml_sort_key):
                root = ET.fromstring(zf.read(name))
                stem = Path(name).stem
                for p_idx, para in enumerate(root.iter(f"{ns}p"), 1):
                    txt = _docx_para_text(para, ns)
                    if txt.strip():
                        units.append({"location": f"{stem}:P{p_idx}", "text": txt})
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": "docx",
            "total_units": len(units),
            "scanned_units": len(units),
            "low_text_pages": [],
            "uncached_formula_cells": [],
            "units": units,
            "doc_type": classify_doc_type([(u["location"], u["text"]) for u in units], ext),
        }

    if ext in {".xlsx", ".xlsm"}:
        openpyxl = _import_openpyxl()
        wb = openpyxl.load_workbook(str(p), data_only=True, read_only=True)
        wb_f = openpyxl.load_workbook(str(p), data_only=False, read_only=True)
        units, uncached = [], []
        try:
            for sname in wb.sheetnames:
                ws, ws_f = wb[sname], wb_f[sname]
                for r_idx, (row, row_f) in enumerate(zip(ws.iter_rows(values_only=True), ws_f.iter_rows(values_only=True)), 1):
                    for c_idx, (val, raw_val) in enumerate(zip(row, row_f), 1):
                        col = openpyxl.utils.get_column_letter(c_idx)
                        coord = f"{sname}!{col}{r_idx}"
                        if val is not None and str(val).strip():
                            units.append({"location": coord, "text": str(val)})
                        elif val is None and isinstance(raw_val, str) and raw_val.startswith("="):
                            uncached.append(coord)
            sheet_cnt = len(wb.sheetnames)
        finally:
            wb.close()
            wb_f.close()
        if uncached:
            sample = ", ".join(uncached[:5]) + ("..." if len(uncached) > 5 else "")
            print(f"WARNING: {len(uncached)} uncached .xlsx formula cell(s) ({sample}).", file=sys.stderr)
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": ext.lstrip("."),
            "total_units": len(units),
            "scanned_units": len(units),
            "sheets": sheet_cnt,
            "low_text_pages": [],
            "uncached_formula_cells": uncached,
            "units": units,
            "doc_type": classify_doc_type([(u["location"], u["text"]) for u in units], ext),
        }

    lines = _read_text_any(p).splitlines()
    units = [{"location": f"Line {i}", "text": l} for i, l in enumerate(lines, 1) if l.strip()]
    return {"schema": "chint-office-extract/v1", "source": str(p), "format": ext.lstrip(".") or "text", "total_units": len(lines), "scanned_units": len(lines), "low_text_pages": [], "uncached_formula_cells": [], "units": units, "doc_type": "text"}


def _read_text_any(p: Path) -> str:
    """Decode text files without silently destroying Chinese content.

    Detection order is BOM first (UTF-8 / UTF-16LE / UTF-16BE), then strict UTF-8, then
    GB18030 (superset of GBK/GB2312). Never use errors="replace": a GBK catalogue decoded
    as UTF-8 with replacement turns every Chinese character into U+FFFD, flips mode to `en`,
    and reports zero findings — the worst possible failure. Never try bare `utf-16`, which
    "succeeds" on any even-length byte blob and produces mojibake.
    """
    data = p.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for enc in ("utf-8", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {p}: tried UTF-8 and GB18030. Convert to UTF-8 and retry.")


TABLE_KW_RE = re.compile(r"\b(?:Icu|Ics|Inm|Icw|Ue|Ui|Uimp)\b|额定|壳架|分断", re.IGNORECASE)


def _extract_page_tables(page, pno: int) -> list[dict]:
    """Extract ruled tables from one PDF page, lazily and only where ratings appear.

    `Page.find_tables()` costs ~50 s across a 120-page catalogue (0.4 s/page), so it is
    gated by TABLE_KW_RE on the page text: 6 candidate pages cost 3.1 s instead of 50 s.
    Returns rows as plain string lists so checks stay stdlib-only.
    """
    out: list[dict] = []
    try:
        found = page.find_tables()
    except Exception:
        return out
    for t_idx, tab in enumerate(getattr(found, "tables", [])):
        try:
            rows = tab.extract()
        except Exception:
            continue
        clean = [[(c or "").replace("\n", " ").strip() for c in row] for row in rows]
        if len(clean) < 2 or max((len(r) for r in clean), default=0) < 2:
            continue
        out.append({"page": pno, "index": t_idx, "rows": clean})
    return out


def _pdf_tables(source: str, pages_filter: set[int] | None = None) -> list[dict]:
    """Keyword-gated table extraction for a PDF (used when the sibling emitted text only)."""
    fitz = _import_fitz()
    out: list[dict] = []
    try:
        doc = fitz.open(source)
    except Exception:
        return out
    try:
        for idx, page in enumerate(doc, 1):
            if pages_filter is not None and idx not in pages_filter:
                continue
            try:
                if not TABLE_KW_RE.search(page.get_text("text")):
                    continue
            except Exception:
                continue
            out.extend(_extract_page_tables(page, idx))
    finally:
        doc.close()
    return out


def load_units(source: str, pages_spec: str | None = None, office_dir: Path | None = None) -> dict:
    pages_filter = parse_page_spec(pages_spec)
    if source != "-":
        p = Path(source)
        if not p.exists():
            raise FileNotFoundError(f"Input not found: {source}")
        _check_not_lfs_pointer(p)
        ext = p.suffix.lower()
        # .doc/.xls/.pptx/.md stay on the built-in path even when the sibling is present:
        # the sibling extractor rejects .doc/.xls outright and knows nothing of pptx/md.
        if ext in {".pdf", ".docx", ".xlsx", ".xlsm"}:
            if office_dir is not None and (office_dir / "scripts" / "extract_doc.py").is_file():
                spec = importlib.util.spec_from_file_location("_chint_office_extract", str(office_dir / "scripts" / "extract_doc.py"))
                if spec is not None and spec.loader is not None:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    obj = mod.extract_document(str(p), mod.parse_page_spec(pages_spec))
                    units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                    tables = obj.get("tables") or []
                    if not tables and ext == ".pdf":
                        # The sibling extractor emits text only; tables are this skill's
                        # concern, so extract them here rather than forking the sibling.
                        tables = _pdf_tables(str(p), pages_filter)
                    return {
                        "source": obj.get("source", source),
                        "format": obj.get("format", ext.lstrip(".")),
                        "office_engine": "sibling:chint-office-suite",
                        "total": obj.get("total_units", len(units)),
                        "scanned": obj.get("scanned_units", len(units)),
                        "low_text_pages": obj.get("low_text_pages", []),
                        "uncached_formula_cells": obj.get("uncached_formula_cells", []),
                        "units": units,
                        "tables": tables,
                        "doc_type": obj.get("doc_type") or classify_doc_type(units, ext),
                    }
        if ext in {".pdf", ".docx", ".xlsx", ".xlsm", ".doc", ".xls", ".pptx", ".md"}:
            obj = _extract_office_builtin(str(p), pages_filter)
            units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
            return {
                "source": obj.get("source", source),
                "format": obj.get("format", ext.lstrip(".")),
                "office_engine": "builtin-standalone",
                "total": obj.get("total_units", len(units)),
                "scanned": obj.get("scanned_units", len(units)),
                "low_text_pages": obj.get("low_text_pages", []),
                "uncached_formula_cells": obj.get("uncached_formula_cells", []),
                "units": units,
                "tables": obj.get("tables", []),
                "doc_type": obj.get("doc_type") or classify_doc_type(units, ext),
            }

    raw = sys.stdin.read() if source == "-" else _read_text_any(Path(source))
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and obj.get("schema") == "chint-office-extract/v1":
                units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                return {
                    "source": obj.get("source", source),
                    "format": obj.get("format", "extract-json"),
                    "office_engine": "pre-extracted-json",
                    "total": obj.get("total_units", len(units)),
                    "scanned": obj.get("scanned_units", len(units)),
                    "low_text_pages": obj.get("low_text_pages", []),
                    "uncached_formula_cells": obj.get("uncached_formula_cells", []),
                    "units": units,
                    "doc_type": obj.get("doc_type") or classify_doc_type(units, ""),
                }
        except json.JSONDecodeError:
            pass
    lines = raw.splitlines()
    units = [(f"Line {i}", l) for i, l in enumerate(lines, 1) if l.strip()]
    return {
        "source": source,
        "format": "text",
        "office_engine": "builtin-standalone",
        "total": len(lines),
        "scanned": len(lines),
        "low_text_pages": [],
        "uncached_formula_cells": [],
        "units": units,
        "doc_type": "text",
    }


def _collect_terms(item: dict) -> list[str]:
    raw: list[str] = []
    if item.get("search"):
        raw.append(str(item["search"]).strip())
    for s in item.get("searches") or []:
        st = str(s).strip()
        if st:
            raw.append(st)
    seen: set[str] = set()
    out: list[str] = []
    for t in raw:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _page_lines_chars(page) -> list[tuple[tuple[float, float, float, float], list[tuple[str, tuple[float, float, float, float]]]]]:
    lines: list[tuple[tuple[float, float, float, float], list[tuple[str, tuple[float, float, float, float]]]]] = []
    raw = page.get_text("rawdict")
    for blk in raw.get("blocks", []):
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            chars: list[tuple[str, tuple[float, float, float, float]]] = []
            for sp in ln.get("spans", []):
                for ch in sp.get("chars", []):
                    c = ch.get("c", "")
                    bbox = ch.get("bbox")
                    if c and bbox:
                        chars.append((c, tuple(bbox)))
            if chars:
                lines.append((tuple(ln["bbox"]), chars))
    return lines


def _chars_in_rect(line_chars, rect) -> list[tuple[int, str, tuple[float, float, float, float]]]:
    hits = []
    for idx, (c, bbox) in enumerate(line_chars):
        cx = (bbox[0] + bbox[2]) * 0.5
        cy = (bbox[1] + bbox[3]) * 0.5
        if (rect.x0 - 1.2) <= cx <= (rect.x1 + 1.2) and (rect.y0 - 1.5) <= cy <= (rect.y1 + 1.5):
            hits.append((idx, c, bbox))
    return hits


def _matching_line(lines, rect):
    ry = (rect.y0 + rect.y1) * 0.5
    best = None
    best_dist = 1e9
    for lb, chars in lines:
        if (lb[0] - 2.0) <= rect.x1 and rect.x0 <= (lb[2] + 2.0) and (lb[1] - 2.0) <= ry <= (lb[3] + 2.0):
            dist = abs((lb[1] + lb[3]) * 0.5 - ry)
            if dist < best_dist:
                best = chars
                best_dist = dist
    return best


def _extract_group_text(lines, group_rects: list) -> tuple[str, bool]:
    """Return text inside rects plus word-boundary pass flag."""
    text_parts: list[str] = []
    first_left_bad = False
    last_right_bad = False
    for g_idx, rect in enumerate(group_rects):
        lchars = _matching_line(lines, rect)
        if not lchars:
            continue
        hits = _chars_in_rect(lchars, rect)
        if not hits:
            continue
        non_ws = [h for h in hits if not h[1].isspace()]
        if not non_ws:
            continue
        text_parts.append("".join(h[1] for h in hits))
        if g_idx == 0:
            first_i, _, first_bb = non_ws[0]
            if first_i > 0:
                prev_c, prev_bb = lchars[first_i - 1]
                if not prev_c.isspace() and prev_c.isascii() and prev_c.isalnum() and (first_bb[0] - prev_bb[2]) < 3.5:
                    first_left_bad = True
        if g_idx == len(group_rects) - 1:
            last_i, _, last_bb = non_ws[-1]
            if last_i + 1 < len(lchars):
                next_c, next_bb = lchars[last_i + 1]
                if not next_c.isspace() and next_c.isascii() and next_c.isalnum() and (next_bb[0] - last_bb[2]) < 3.5:
                    last_right_bad = True
    return "".join(text_parts), (first_left_bad or last_right_bad)


def _group_multiline_rects(raw_rects: list, lines, term: str) -> list[list]:
    """Group PyMuPDF rects belonging to one wrapped phrase into single occurrences."""
    target_norm = re.sub(r"\s+", "", term)
    if not raw_rects:
        return []
    groups: list[list] = []
    acc_rects: list = []
    acc_norm_len = 0
    for r in raw_rects:
        lchars = _matching_line(lines, r)
        seg = "".join(h[1] for h in _chars_in_rect(lchars, r)) if lchars else ""
        seg_norm_len = len(re.sub(r"\s+", "", seg))
        acc_rects.append(r)
        acc_norm_len += seg_norm_len if seg_norm_len > 0 else len(target_norm)
        if acc_norm_len >= len(target_norm):
            groups.append(acc_rects)
            acc_rects = []
            acc_norm_len = 0
    if acc_rects:
        groups.append(acc_rects)
    return groups


def _find_occurrence_groups(page, lines, terms: list[str], whole_word: bool | None, case_sensitive: bool | None) -> list[list]:
    seen: set[tuple[tuple[float, float, float, float], ...]] = set()
    accepted: list[list] = []
    for t in terms:
        ww = whole_word if whole_word is not None else bool(t and ((t[0].isascii() and t[0].isalnum()) or (t[-1].isascii() and t[-1].isalnum())))
        cs = case_sensitive if case_sensitive is not None else (len(t) <= 4 and any(c.isupper() for c in t) and t == t.upper())
        raw_rects = page.search_for(t)
        for grp in _group_multiline_rects(raw_rects, lines, t):
            g_text, _ = _extract_group_text(lines, grp)
            if g_text:
                if cs:
                    t_compact = re.sub(r"\s+", "", t)
                    g_compact = re.sub(r"\s+", "", g_text)
                    if t_compact not in g_compact:
                        continue
                if ww:
                    lchars_0 = _matching_line(lines, grp[0])
                    lchars_n = _matching_line(lines, grp[-1])
                    bad_edge = False
                    if t[0].isascii() and t[0].isalnum() and lchars_0:
                        hits0 = [h for h in _chars_in_rect(lchars_0, grp[0]) if not h[1].isspace()]
                        if hits0 and hits0[0][0] > 0:
                            pc, pbb = lchars_0[hits0[0][0] - 1]
                            if pc.isascii() and pc.isalnum() and (hits0[0][2][0] - pbb[2]) < 3.5:
                                bad_edge = True
                    if t[-1].isascii() and t[-1].isalnum() and lchars_n:
                        hitsn = [h for h in _chars_in_rect(lchars_n, grp[-1]) if not h[1].isspace()]
                        if hitsn and hitsn[-1][0] + 1 < len(lchars_n):
                            nc, nbb = lchars_n[hitsn[-1][0] + 1]
                            if nc.isascii() and nc.isalnum() and (nbb[0] - hitsn[-1][2][2]) < 3.5:
                                bad_edge = True
                    if bad_edge:
                        continue
            sig = tuple((round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)) for r in grp)
            if sig not in seen:
                seen.add(sig)
                accepted.append(grp)
    return accepted


def _annotate_pdf_builtin(input_pdf: Path, items: list[dict], output_pdf: Path, default_author: str = "CHINT Catalog Edit") -> dict:
    fitz = _import_fitz()
    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    if output_pdf.resolve() == input_pdf.resolve():
        raise ValueError("Refusing to overwrite input PDF; choose a distinct output path.")

    doc = fitz.open(str(input_pdf))
    try:
        if doc.is_encrypted:
            raise ValueError(f"PDF '{input_pdf}' is encrypted/password-protected; decrypt before annotation.")
        matched_items, highlights, rect_count, stickies = 0, 0, 0, 0
        page_stickies: dict[int, int] = {}
        page_line_cache: dict[int, list] = {}
        fallback_items: list[dict] = []

        for idx, item in enumerate(items, 1):
            if not isinstance(item, dict) or "page" not in item:
                raise ValueError(f"Annotation #{idx} missing required 'page' field.")
            pno = int(item["page"])
            if pno < 1 or pno > len(doc):
                raise ValueError(f"Annotation #{idx} page {pno} out of range 1..{len(doc)}")
            page = doc[pno - 1]
            if pno not in page_line_cache:
                page_line_cache[pno] = _page_lines_chars(page)
            terms = _collect_terms(item)
            comment = str(item.get("comment", "")).strip()
            author = str(item.get("author") or default_author)
            mode = str(item.get("match_mode") or "all").lower()
            if mode not in {"all", "merged", "first"}:
                raise ValueError(f"Annotation #{idx} invalid match_mode: {mode}")
            ww = item.get("whole_word")
            cs = item.get("case_sensitive")

            occ_groups = _find_occurrence_groups(page, page_line_cache[pno], terms, ww, cs)
            if occ_groups:
                matched_items += 1
                if mode == "merged":
                    flat_rects = [r for grp in occ_groups for r in grp]
                    annot = page.add_highlight_annot(flat_rects)
                    annot.set_colors(stroke=YELLOW)
                    annot.set_info(title=author, content=comment)
                    annot.update()
                    highlights += 1
                    rect_count += len(flat_rects)
                else:
                    targets = [occ_groups[0]] if mode == "first" else occ_groups
                    for grp in targets:
                        annot = page.add_highlight_annot(grp)
                        annot.set_colors(stroke=YELLOW)
                        annot.set_info(title=author, content=comment)
                        annot.update()
                        highlights += 1
                        rect_count += len(grp)
            else:
                idx_on_page = page_stickies.get(pno, 0)
                page_stickies[pno] = idx_on_page + 1
                prect = page.rect
                rows_per_col = max(1, int((prect.height - 32) // 22))
                col = idx_on_page // rows_per_col
                row = idx_on_page % rows_per_col
                x = prect.x0 + 16 if col == 0 else max(prect.x0 + 16, prect.x1 - 34 - (col - 1) * 24)
                y = min(prect.y1 - 24, prect.y0 + 16 + row * 22)
                label = terms[0] if len(terms) == 1 else (", ".join(terms[:3]) + (" 等" if len(terms) > 3 else "") if terms else "")
                note_body = f"[{label}] {comment}" if label else comment
                annot = page.add_text_annot(fitz.Point(x, y), note_body)
                annot.set_colors(stroke=YELLOW)
                annot.set_info(title=author, content=note_body)
                annot.update()
                stickies += 1
                fallback_items.append({"page": pno, "label": label, "comment": comment})

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_pdf))
        return {
            "schema": "chint-office-annotate/v1",
            "office_engine": "builtin-standalone",
            "input": str(input_pdf),
            "output": str(output_pdf),
            "total": len(items),
            "matched_items": matched_items,
            "highlight_annotations": highlights,
            "highlighted_rects": rect_count,
            "sticky_fallback_count": stickies,
            "fallback_items": fallback_items,
        }
    finally:
        doc.close()


def write_annotated_pdf(
    input_pdf: Path,
    items: list[dict],
    output_pdf: Path,
    default_author: str = "CHINT Catalog Edit",
    office_dir: Path | None = None,
) -> dict:
    if office_dir is not None and (office_dir / "scripts" / "annotate_pdf.py").is_file():
        spec = importlib.util.spec_from_file_location("_chint_office_annotate", str(office_dir / "scripts" / "annotate_pdf.py"))
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            res = mod.annotate_pdf(input_pdf, items, output_pdf, default_author=default_author)
            res["office_engine"] = "sibling:chint-office-suite"
            return res
    return _annotate_pdf_builtin(input_pdf, items, output_pdf, default_author=default_author)


# ---------------------------------------------------------------------------
# L1 / L2 Catalogue Rules
# ---------------------------------------------------------------------------

CATALOG_RULES_PATH = Path(__file__).resolve().parent.parent / "references" / "catalog_rules.json"
_catalog_rules_cache: dict | None = None


def load_catalog_rules(path: Path | None = None) -> dict:
    """Load externalized rule data (typos, synonym groups, notation rules).

    Product-line vocabulary lives in catalog_rules.json, never in this script;
    add new entries there instead of patching single-catalogue cases here.
    """
    global _catalog_rules_cache
    if path is None and _catalog_rules_cache is not None:
        return _catalog_rules_cache
    rules_path = path or CATALOG_RULES_PATH
    try:
        data = json.loads(rules_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing rule data file: {rules_path}") from exc
    required = ("zh_typos", "same_page_conflicts", "cross_page_synonyms", "case_notation")
    missing = [k for k in required if k not in data]
    if missing:
        raise RuntimeError(f"Rule data file {rules_path} missing keys: {missing}")
    if path is None:
        _catalog_rules_cache = data
    return data


# Generic detectors: deliberately carry no catalogue-specific vocabulary so they
# generalize to any product line. Product vocabulary belongs in catalog_rules.json.
# Bounds may carry comma or space group separators (`12,500`, `12 500`) — GB/T 15835 5.1.1
# treats the space form as the standard's own typography, so grouping must not be split.
_NUM_GROUP = r"[+\-−]?\d{1,3}(?:(?:[,\u00a0 ]\d{3})+)(?:\.\d+)?|[+\-−]?\d+(?:\.\d+)?"
# Connectors: ～ ~ 至 plus hyphen/en-dash. `100-63A` is the single most common written
# inverted range, and it was invisible because only CJK connectors were accepted.
RANGE_RE = re.compile(r"(" + _NUM_GROUP + r")\s*[~～至\-–—]\s*(" + _NUM_GROUP + r")")
# Relative-multiple suffix after the second bound: `40 ～ 1.2In` / `0.4～1.0Un`.
# Internal sanity heuristic only — GB/T 15835 governs connector choice, not magnitude order.
# Only relative symbols are multipliers. A trailing plain unit (`100-63A`) is the same
# scale as the first bound, so the two numbers remain comparable.
RANGE_MULTIPLIER_RE = re.compile(r"^\s*(?:In|Ir|Iu|Icu|Ics|Isd|Icw|Un|Ue|Ui|Uimp)\b")
# A hyphen range must be followed by a unit to be a range rather than a model code.
HYPHEN_RANGE_UNIT_RE = re.compile(
    r"^\s*(?:k?VA|k?A|k?V|k?W|MVA|VA|kVAR|kvar|mm|cm|kg|℃|°C|%|％|kHz|MHz|Hz|ms|min|h|s)"
    r"(?![A-Za-z0-9])"
)
# Clock spans (`00:00~24:00`): the range regex sees only the seconds field.
CLOCK_RANGE_RE = re.compile(r"\d{1,2}:\d{2}\s*[~～至-]\s*\d{1,2}:\d{2}")
# Hexadecimal literals (`0x03~0x64`): the range regex stops at the `0` of `0x64` and
# reports `03~0` as a zero-bounded range. Modbus register and address spans are written
# this way constantly, so the hex form must be recognised before the numeric check.
HEX_RANGE_RE = re.compile(r"0[xX][0-9A-Fa-f]+\s*[~～至\-–—]\s*0[xX][0-9A-Fa-f]+")
DUP_WORD_ZH_RE = re.compile(r"([一-鿿]{2,6})\1")
DUP_WORD_EN_RE = re.compile(r"\b([A-Za-z]{3,})\s+\1(?![-\w])", re.IGNORECASE)
ICS_RE = re.compile(r"\bIcs\b\s*(?:=|:|：|≤|≥|>=|>)?\s*(\d+(?:\.\d+)?)\s*(kA|A)?", re.IGNORECASE)
ICU_RE = re.compile(r"\bIcu\b\s*(?:=|:|：|≤|≥|>=|>)?\s*(\d+(?:\.\d+)?)\s*(kA|A)?", re.IGNORECASE)
# Order-aware pair: catalogues write both `Icu/Ics 65/50` and `Ics/Icu 65/50`; the symbol
# order decides which number is the limiting rating. Hard-coding Icu/Ics first silently
# skipped the inversion check on the equally common reverse form.
ICU_ICS_PAIR_RE = re.compile(
    r"\b(Icu|Ics)\s*/\s*(Icu|Ics)\b\s*(?:=|:|：)?\s*(\d+(?:\.\d+)?)\s*(?:kA|A)?\s*/\s*(\d+(?:\.\d+)?)\s*(?:kA|A)?",
    re.IGNORECASE,
)
# Require an explicit value separator: `\bIn\b` alone matches the English preposition,
# which fabricated "In must not exceed Inm" hard errors on ordinary prose.
_IN_SEP = r"\s*(?:=|:|：|≤|≥|<=|>=)\s*"
IN_RE = re.compile(r"(?<![A-Za-z])In" + _IN_SEP + r"(\d+(?:\.\d+)?)\s*(kA|A)\b")
INM_RE = re.compile(r"(?<![A-Za-z])Inm\s*(?:=|:|：|≤|≥|<=|>=)?\s*(\d+(?:\.\d+)?)\s*(kA|A)\b")
UE_RE = re.compile(r"(?<![A-Za-z])Ue" + _IN_SEP + r"(\d+(?:\.\d+)?)\s*(kV|V)\b")
UI_RE = re.compile(r"(?<![A-Za-z])Ui" + _IN_SEP + r"(\d+(?:\.\d+)?)\s*(kV|V)\b")
PAGE_REF_ZH_RE = re.compile(r"(?:详见|参见|参阅)\s*P0*(\d+)\b|见第\s*0*(\d+)\s*页")
PAGE_REF_EN_RE = re.compile(r"\b(?:see|refer\s+to)\s+(?:page|p\.)\s*(\d+)\b", re.IGNORECASE)
# CJK 图/表 plus English Fig./Figure/Table. English catalogues previously had exactly
# zero captions parsed, so the duplicate/gap checks were dead on every EN document.
CAPTION_RE = re.compile(
    r"^(?:([图表])|(Fig(?:ure)?|Tab(?:le)?)\.?)\s*(\d+(?:[-–—.]\d+)*)(?![0-9A-Za-z])",
    re.IGNORECASE,
)
CAPTION_REF_TAIL_RE = re.compile(r"^(?:所示|中|为|和|与|及|的|见|可|所)")
# Enumerated list markers / numeric footnote refs: `1)` `a)` `(1)` `509)` `651)/702)`,
# including superscript footnote refs glued to a word by text extraction (`ETU15B1)`).
# A closer that ends one of these is typography, not an unmatched bracket.
LIST_MARKER_TAIL_RE = re.compile(
    r"(?:^|[\s（(,])(?:\d{1,4}[a-zA-Z]?|[a-zA-Z]\d{0,4})[)）](?:\s*[/、,]\s*\d{1,4}[)）])*\s*(?:\S|$)"
)
# Trailing superscript footnote marker: `ETU15B1)`, `✔2)`, `--1)`, `breakers3)`.
FOOTNOTE_TAIL_RE = re.compile(r"(?:[^\s(（][\dA-Za-z])[)）]\s*$")


def _num(text: str) -> float:
    return float(text.replace("−", "-").replace(",", "").replace("\u00a0", "").replace(" ", ""))


def _scaled_pair(m1, m2) -> tuple[float, float] | None:
    """Compare two same-dimension quantities (A/kA or V/kV); None if dimensions differ."""
    scale = {"a": 1.0, "ka": 1e3, "v": 1.0, "kv": 1e3}
    u1, u2 = m1.group(2).lower(), m2.group(2).lower()
    if (u1 in ("a", "ka")) != (u2 in ("a", "ka")):
        return None
    return _num(m1.group(1)) * scale[u1], _num(m2.group(1)) * scale[u2]


def _is_legit_reduplication(line: str, m) -> bool:
    """True when a doubled Chinese token is a legitimate compound, not a typo.

    `过载长延时延时时间` reads as 长延时 + 延时时间. Exceptions are data-driven in
    `catalog_rules.json` so a product line can add its own without touching Python.
    """
    before = line[max(0, m.start() - 6): m.start()]
    after = line[m.end(): m.end() + 6]
    for exc in load_catalog_rules().get("duplicate_word_exceptions", []):
        if exc.get("pattern") and exc["pattern"] not in m.group(0):
            continue
        pre = exc.get("unless_preceded_by")
        post = exc.get("unless_followed_by")
        if pre and not before.endswith(pre):
            continue
        if post and not after.startswith(post):
            continue
        return True
    return False


def _max_page(units: list[tuple[str, str]]) -> int:
    pages = [int(m.group(1)) for loc, _ in units if (m := re.match(r"^P(\d+):", loc))]
    return max(pages, default=0)


def _caption_key(text: str) -> tuple[str, str] | None:
    """Return (kind, normalized number) for figure/table caption-like units only."""
    s = text.strip()
    m = CAPTION_RE.match(s)
    if not m or len(s) > 60:
        return None
    if CAPTION_REF_TAIL_RE.match(s[m.end():].strip()):
        return None
    num = re.sub(r"[\s–—.]", "-", m.group(3))
    kind = "图" if m.group(1) == "图" else ("表" if m.group(1) == "表" else m.group(2)[:3].lower())
    return kind, num


_PAGE_LOC_RE = re.compile(r"^P\d+:")

HIGH_CATS = {
    "TECH_HARD_ERROR",
    "TYPO_GRAMMAR_ZH",
    "CROSSREF_NUMBERING",
    "SAME_PAGE_INCONSISTENCY",
    "EN_SEVERE_ERROR",
    "COMPETITOR_CODE",
    "STD_CONCEPT_ERROR",
    "OBSOLETE_CLAUSE_ED5",
    "UNRESOLVED_SLOT",
    "DUPLICATE_WORD",
    "NUMERIC_RANGE",
    "BRACKET_UNBALANCED",
}


def detect_mode(units: list[tuple[str, str]]) -> str:
    sample = " ".join(txt for _, txt in units[:200])
    cjk = len(re.findall(r"[\u4e00-\u9fff]", sample))
    lat = len(re.findall(r"[A-Za-z]", sample))
    if cjk == 0 and lat > 0:
        return "en"
    if cjk >= max(2, int(0.15 * (cjk + lat))):
        return "zh"
    return "en"


def _page_key(loc: str) -> str:
    m = re.match(r"^(P\d+):", loc)
    return m.group(1) if m else "__all__"


def _severity(cat: str) -> str:
    return "HIGH" if cat in HIGH_CATS else "MEDIUM"


# ---------------------------------------------------------------------------
# Table-level checks (find_tables, gated by keyword; see _extract_page_tables)
# ---------------------------------------------------------------------------

_ROW_SYMBOL_RE = re.compile(r"\b(Icu|Ics)\b", re.IGNORECASE)
_PLAIN_NUM_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:kA)?\s*$")


def _numeric_cells(row: list[str]) -> dict[int, float]:
    """Column index -> value for cells that are a bare number (optionally with kA)."""
    out: dict[int, float] = {}
    for i, cell in enumerate(row):
        m = _PLAIN_NUM_RE.match(cell or "")
        if m:
            out[i] = float(m.group(1))
    return out


def _table_findings(tables: list[dict]) -> list[dict]:
    """Detect Ics > Icu when the two ratings sit on separate rows of the same table.

    The line-level detector needs both symbols on one line. In a ruled ratings table
    `Rated Ultimate ... (Icu)` and `Rated Service ... (Ics)` are different rows whose
    numeric cells share column positions, so they are paired by column index.

    Rows are accepted only when they literally carry `Icu` / `Ics`; a label-text
    heuristic previously matched `Service Life` and fabricated 15000 > 42.
    """
    out: list[dict] = []
    for t in tables:
        prev_icu: dict[int, float] | None = None
        for row in t["rows"]:
            blob = " ".join(c for c in row if c)
            sym = _ROW_SYMBOL_RE.search(blob)
            if not sym:
                prev_icu = None
                continue
            cells = _numeric_cells(row)
            if sym.group(1).lower() == "icu":
                prev_icu = cells
                continue
            # Pair only with the Icu row directly above. A page holds several independent
            # rating blocks (main / earthing switch / 1150 V); cross-pairing them fabricated
            # `Ics 65 > Icu 30` from unrelated sections.
            if prev_icu is not None:
                for col in sorted(set(cells) & set(prev_icu)):
                    a, b = cells[col], prev_icu[col]
                    if a > b:
                        out.append({
                            "location": f"P{t['page']}:Table",
                            "severity": "HIGH",
                            "category": "TECH_HARD_ERROR",
                            "match": "Icu / Ics",
                            "fix": f"表列 {col + 1}：Ics {a:g} 不得大于 Icu {b:g}（IEC 60947-2 / GB/T 14048.2）",
                            "excerpt": f"P{t['page']} 表列 {col + 1}",
                            "_full_line": "",
                            "_table_col": col + 1,
                        })
            prev_icu = None
    return out


def scan_units(
    units: list[tuple[str, str]],
    profile: str = "L1",
    mode: str = "auto",
    with_iec: bool = False,
    dept: str = "all",
    ssot: dict | None = None,
    total_pages: int | None = None,
    tables: list[dict] | None = None,
    external_reference: bool = False,
) -> list[dict]:
    if mode == "auto":
        mode = detect_mode(units)
    if ssot is None:
        ssot, _, _ = load_translation_ssot(resolve_translation_skill())
    rules = load_catalog_rules()
    if total_pages is None:
        total_pages = _max_page(units)
    downgrade_terms = tuple(
        t.lower() for t in rules.get("severity_overrides", {}).get("downgrade_if_pattern_contains", [])
    )

    # Competitor codes (MX/XF/MN/SDE/MCH/KLC) are CHINT-internal reminders: their fix is a
    # CHINT code. Only suppress them when --external-reference is passed OR the document has
    # zero CHINT identifiers and multiple peer brand mentions (>=3 in the first 400 units),
    # so a CHINT catalogue mentioning a competitor once does not disable competitor checks.
    brands_re = re.compile(r"\b(?:ABB|Schneider|Siemens|LS|Legrand|Eaton|Hager|Mitsubishi|"
                           r"Moeller|Terasaki|Hyundai|Westinghouse|GE|Fuji|Toshiba)\b", re.IGNORECASE)
    chint_re = re.compile(r"(?:CHINT|正泰|\b(?:NX[AMFC]\d|NA\d|NM\d|NB\d|NC\d))", re.IGNORECASE)
    doc_blob = " ".join(txt for _, txt in units[:400])
    ssot = dict(ssot)
    ssot["external_document"] = bool(
        external_reference or (not chint_re.search(doc_blob) and len(brands_re.findall(doc_blob)) >= 3)
    )

    run_l2 = profile in {"L2", "L3"}
    run_iec_concept = with_iec or profile == "L3"
    run_iec_statutory = with_iec or profile == "L3"

    findings: list[dict] = []

    def add(loc: str, cat: str, matched: str, fix: str, line: str) -> None:
        findings.append({
            "location": loc,
            "severity": _severity(cat),
            "category": cat,
            "match": matched,
            "fix": fix,
            "excerpt": line[:120],
            "_full_line": line,
        })

    ed5_re = ssot.get("ED5_CLAUSE_RE")
    ed5_guards = ssot.get("ED5_GUARD_TAGS", ())
    pf_context_re = re.compile(r"(?i)power\s+factor|\bcos\s*[φϕ]?|功率因数")
    cat_a_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*A\b|选择性类别[ \t]*[:：]?[ \t]*A\b)(?![ \t]*[/、,])", re.IGNORECASE)
    cat_b_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*B\b|选择性类别[ \t]*[:：]?[ \t]*B\b|\bCategory[ \t]+B\b)", re.IGNORECASE)
    model_hdr_re = re.compile(r"^\s*(?:NX[AMF]\d|NM\d|NA\d|DW\d)")
    st_re = re.compile(r"\bIsd\b")
    icw_re = re.compile(r"\bIcw\b")
    type_fb_re = re.compile(r"\bType[ \t]+(?:F|B\+)\b", re.IGNORECASE)

    blocks: dict[str, list[tuple[str, str]]] = {}
    for loc, line in units:
        # Page-scoped units group by page; everything else (docx paragraphs, text lines,
        # JSON extracts) groups as one document block. Previously this fell back to one
        # block per line once a document exceeded 40 units, which silently disabled every
        # cross-line detector (same-page conflicts, bracket balance, AC/DC pairs, A+Isd).
        bkey = _page_key(loc) if _PAGE_LOC_RE.match(loc) else "__all__"
        blocks.setdefault(bkey, []).append((loc, line))

    for loc, line in units:
        for rule in rules["zh_typos"]:
            for m in re.finditer(rule["pattern"], line):
                add(loc, "TYPO_GRAMMAR_ZH", m.group(0), rule["fix"], line)

        for m in DUP_WORD_ZH_RE.finditer(line):
            if _is_legit_reduplication(line, m):
                continue
            add(loc, "DUPLICATE_WORD", m.group(0), m.group(1), line)
        for m in DUP_WORD_EN_RE.finditer(line):
            add(loc, "DUPLICATE_WORD", m.group(0), m.group(1), line)

        for m in RANGE_RE.finditer(line):
            # Clock times (`00:00~24:00`) are not numeric parameter ranges; the range regex
            # captures only the seconds field, so inspect the surrounding span.
            span = line[max(0, m.start() - 3): m.end() + 3]
            if CLOCK_RANGE_RE.search(span):
                continue
            # Hex spans (`0x03~0x64`) look like `03~0` to the numeric regex, which then
            # reports a zero-bounded range. Widen the span past the trailing hex digits.
            if HEX_RANGE_RE.search(line[max(0, m.start() - 3): m.end() + 5]):
                continue
            connector = line[m.start(2) - 1: m.start(2)].strip() or "-"
            if connector in "-–—":
                # Hyphen ranges are only ranges when a unit follows (`100-63A`). Without one
                # they are model codes and standard numbers: `NXA16S-AC240-3P+N`, `IEC 60947-2`,
                # `3WL 9 111-0` catalogue order numbers.
                if not HYPHEN_RANGE_UNIT_RE.search(line[m.end():]):
                    continue
                # GB/T 15835 5.1.3 permits eliding the unit on the first bound, so
                # `100-63A` and `30-3V` share one shape. Descending order is reported for
                # both; the reviewer decides from page context.
                if m.start() > 0 and re.match(r"[/A-Za-z0-9]", line[m.start() - 1]):
                    continue
            lo, hi = _num(m.group(1)), _num(m.group(2))
            if hi == 0:
                # A zero bound is never a denominator; report it directly instead of
                # dividing (was: float division by zero crashed the whole run).
                add(loc, "NUMERIC_RANGE", m.group(0), "区间含 0 值界限，核实是否漏写单位或范围", line)
                continue
            # A relative-multiple suffix (`1.2In`) means the bounds are different scales.
            # The old magnitude ratio gate (`lo/hi >= 20`) swallowed the worst real
            # inversions (6300~250A); suffix presence is the actual signal.
            if RANGE_MULTIPLIER_RE.search(line[m.end():]):
                continue
            if lo > hi:
                add(loc, "NUMERIC_RANGE", m.group(0), "区间上下限倒挂，改为「下限~上限」", line)
            elif lo == hi and not re.search(r"[+\-−]", m.group(0)[1:]):
                add(loc, "NUMERIC_RANGE", m.group(0), "单值区间（上下限相同），核实是否漏写范围", line)

        m_pair = ICU_ICS_PAIR_RE.search(line)
        m_ics, m_icu = ICS_RE.search(line), ICU_RE.search(line)
        if m_pair:
            sym_a, sym_b = m_pair.group(1).lower(), m_pair.group(2).lower()
            val = {sym_a: _num(m_pair.group(3)), sym_b: _num(m_pair.group(4))}
            if "ics" in val and "icu" in val and val["ics"] > val["icu"]:
                add(loc, "TECH_HARD_ERROR", m_pair.group(0), "Ics 不得大于 Icu（IEC 60947-2 / GB/T 14048.2）", line)
        elif m_ics and m_icu and m_ics.group(2) == m_icu.group(2) and _num(m_ics.group(1)) > _num(m_icu.group(1)):
            add(loc, "TECH_HARD_ERROR", f"{m_ics.group(0)} + {m_icu.group(0)}", "Ics 不得大于 Icu（IEC 60947-2 / GB/T 14048.2）", line)

        for m_a, m_b, fix in (
            (IN_RE.search(line), INM_RE.search(line), "In 不得超过壳架等级额定电流（GB/T 14048.2—2020 Cl. 2.1.1 壳架等级；Inm 为行业惯用符号，标准未定义）"),
            (UE_RE.search(line), UI_RE.search(line), "Ue 不得超过额定绝缘电压 Ui（GB/T 14048.2—2020 / IEC 60947-2:2024）"),
        ):
            if m_a and m_b:
                pair = _scaled_pair(m_a, m_b)
                if pair and pair[0] > pair[1]:
                    add(loc, "TECH_HARD_ERROR", f"{m_a.group(0)} + {m_b.group(0)}", fix, line)

        for m in re.finditer(r"Ui\s*\(\s*kV\s*\)", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "Ui(V)（额定绝缘电压单位应为 V，与 Uimp(kV) 互倒）", line)
        for m in re.finditer(r"Uimp\s*\(\s*V\s*\)", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "Uimp(kV)（额定冲击耐受电压单位应为 kV，与 Ui(V) 互倒）", line)
        for m in re.finditer(r"直流\s*[（(][^）)]*AC\s*\d+\s*V[^）)]*[）)]", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "核改直流电压代号（直流括号内误写 AC 电压）", line)
        for m in re.finditer(r"交流\s*[（(][^）)]*DC\s*\d+\s*V[^）)]*[）)]", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "核改交流电压代号（交流括号内误写 DC 电压）", line)

        m_page = re.match(r"^P(\d+):", loc)
        cur_p = int(m_page.group(1)) if m_page else 0
        if cur_p:
            for m_ref in PAGE_REF_ZH_RE.finditer(line):
                ref = int(m_ref.group(1) or m_ref.group(2))
                if ref == cur_p:
                    add(loc, "CROSSREF_NUMBERING", m_ref.group(0), f"修正交叉引用页码（第 {cur_p} 页不应自引本页）", line)
                elif total_pages and ref > total_pages:
                    # Printed folio ≠ PDF page index (a 34-page file can print "P036"), so
                    # this is a "verify", not a proven error.
                    add(loc, "CROSSREF_NUMBERING", m_ref.group(0),
                        f"引用页码 {ref} 大于 PDF 页数 {total_pages}（印刷页码与 PDF 索引常不同），核对", line)
            for m_ref in PAGE_REF_EN_RE.finditer(line):
                ref = int(m_ref.group(1))
                if ref == cur_p:
                    add(loc, "CROSSREF_NUMBERING", m_ref.group(0), f"Page {cur_p} must not reference itself", line)
                elif total_pages and ref > total_pages:
                    add(loc, "CROSSREF_NUMBERING", m_ref.group(0), f"Page reference exceeds total {total_pages} pages", line)
        for m in re.finditer(r"\{\{[^}]+\}\}", line):
            add(loc, "UNRESOLVED_SLOT", m.group(0), "补填数据表核实值或改为定性描述", line)

        if mode == "en":
            raw_bl = list(ssot.get("BLACKLIST_COMMON", []))
            if dept in {"acb", "all"}:
                raw_bl.extend(ssot.get("BLACKLIST_ACB", []))
            if dept in {"mccb", "all"}:
                raw_bl.extend(ssot.get("BLACKLIST_MCCB", []))
            bl: list[tuple[str, str]] = []
            seen_bl_pats: set[str] = set()
            for pat, fix in raw_bl:
                if pat not in seen_bl_pats:
                    seen_bl_pats.add(pat)
                    bl.append((pat, fix))
            for pat, fix in bl:
                downgraded = any(t in pat.lower() for t in downgrade_terms)
                if downgraded and not run_l2:
                    continue
                cat = "EN_TERM_CONSISTENCY" if downgraded else "EN_SEVERE_ERROR"
                for m in re.finditer(pat, line, re.IGNORECASE):
                    add(loc, cat, m.group(0), fix, line)
            # Competitor accessory codes only mean something in a CHINT document; running
            # them on a Schneider/ABB catalogue reports 100 % false positives.
            comp_rules = [] if ssot.get("external_document") else list(ssot.get("COMPETITOR_RULES_COMMON", []))
            if dept in {"acb", "all"} and comp_rules:
                comp_rules.extend(ssot.get("COMPETITOR_RULES_ACB", []))
            for c_pat, c_fix in comp_rules:
                for m in re.finditer(c_pat, line):
                    if "(PF)" in m.group(0).upper() and pf_context_re.search(line):
                        continue
                    add(loc, "COMPETITOR_CODE", m.group(0), c_fix, line)

        if run_l2:
            for rule in rules["case_notation"]:
                for m in re.finditer(rule["pattern"], line):
                    add(loc, "SYMBOL_CASE_NOTATION", m.group(0), rule["fix"], line)

        if run_iec_concept:
            if mode == "zh":
                for pat, fix in ssot.get("STD_CONCEPT_ZH", []):
                    for m in re.finditer(pat, line):
                        add(loc, "STD_CONCEPT_ERROR", m.group(0), fix, line)
            if mode == "en" and ed5_re is not None:
                for m in ed5_re.finditer(line):
                    window = line[max(0, m.start() - 80):min(len(line), m.end() + 40)]
                    if not any(tag in window for tag in ed5_guards):
                        add(loc, "OBSOLETE_CLAUSE_ED5", m.group(0), "按 IEC 60947-2:2024 第 6 版核改条款号", line)

        if run_iec_statutory and mode == "zh":
            for pat, fix in ssot.get("STD_STATUTORY_ZH", []):
                for m in re.finditer(pat, line):
                    add(loc, "STD_STATUTORY_ZH", m.group(0), fix, line)

    caption_hits: dict[tuple[str, str], list[str]] = {}
    for items in blocks.values():
        page_blob = "\n".join(txt for _, txt in items)

        # Generic bracket pairing: cumulative balance catches closers that precede any
        # opener, including full-width forms and closers stranded on a wrapped line.
        # Enumerated list markers (`1)` / `a)` / `(1)` sequences without an opener) are
        # legitimate typography, not unbalanced brackets -- skip them.
        balance = 0
        last_open_loc = None
        for loc, txt in items:
            for i, ch in enumerate(txt):
                if ch in "(（":
                    balance += 1
                    last_open_loc = (loc, i)
                elif ch in ")）":
                    balance -= 1
                    if balance < 0:
                        prefix = txt[: i + 1].rstrip()
                        if LIST_MARKER_TAIL_RE.search(prefix) or FOOTNOTE_TAIL_RE.search(prefix):
                            balance = 0
                            continue
                        add(loc, "BRACKET_UNBALANCED", txt[max(0, i - 10):i + 1], "括号不配对（多出右括号）", txt)
                        balance = 0
        # Openers left unclosed at page end. Previously only surplus closers were reported,
        # so a line like `(−45~40)℃` with a dropped `(` stayed invisible.
        if balance > 0 and last_open_loc is not None:
            o_loc, o_idx = last_open_loc
            o_txt = next(t for l, t in items if l == o_loc)
            add(o_loc, "BRACKET_UNBALANCED", o_txt[max(0, o_idx - 10): o_idx + 11], "括号不配对（左括号未闭合）", o_txt)

        for loc, txt in items:
            cap = _caption_key(txt)
            if cap:
                caption_hits.setdefault(cap, []).append(loc)

        for idx in range(len(items) - 1):
            loc1, t1 = items[idx]
            _, t2 = items[idx + 1]
            pair_txt = t1 + " " + t2
            for kind, bad, good in (("直流", "AC", "DC"), ("交流", "DC", "AC")):
                m_pair = re.search(rf"({kind}\s*[（(][^）)]*)\s+({bad}\s*\d+\s*V[^）)]*[）)])", pair_txt)
                if re.search(rf"{kind}\s*[（(][^）)]*$", t1) and re.search(rf"^\s*{bad}\s*\d+\s*V[^）)]*[）)]", t2):
                    matched_frag = f"{m_pair.group(1)} {m_pair.group(2)}" if m_pair else f"{t1.strip()} {t2.strip()}"
                    add(loc1, "TECH_HARD_ERROR", matched_frag, f"{kind}电压括号内误写 {bad} 电压（应为 {good}）", pair_txt)

        for idx, (loc, txt) in enumerate(items):
            m_a = cat_a_re.search(txt)
            if m_a:
                win_lines = []
                if idx > 0 and not cat_b_re.search(items[idx - 1][1]):
                    win_lines.append(items[idx - 1][1])
                win_lines.append(txt)
                for fwd in range(idx + 1, min(len(items), idx + 4)):
                    ntxt = items[fwd][1]
                    if cat_b_re.search(ntxt) or model_hdr_re.search(ntxt):
                        break
                    win_lines.append(ntxt)
                win_blob = "\n".join(win_lines)
                m_st = st_re.search(win_blob)
                if m_st and not icw_re.search(win_blob):
                    add(
                        loc,
                        "TECH_HARD_ERROR",
                        f"{m_a.group(0)} + {m_st.group(0)}",
                        "选择性类别 A 配人为短延时（Isd）须声明经试验程序 IV 验证的 Icw（或改选选择性类别 B 并按 IEC 表 2 / GB 表 3 声明 Icw，IEC 5.4 / GB 4.4）",
                        txt,
                    )

            m_fb = type_fb_re.search(txt)
            if m_fb:
                lo, hi = max(0, idx - 2), min(len(items), idx + 3)
                local_blob = "\n".join(t for _, t in items[lo:hi])
                if re.search(r"60947-2", local_blob) and not re.search(r"62423|\b(?:VDE\s*)?0664", local_blob):
                    add(loc, "TECH_HARD_ERROR", f"{m_fb.group(0)} + IEC 60947-2", "IEC 60947-2 附录 B 仅覆盖 AC/A/B 型；Type F/B+ 须引 IEC 62423", txt)

        for group in rules["same_page_conflicts"]:
            present: list[tuple[str, str]] = []
            for variant in group["variants"]:
                for loc, txt in items:
                    if re.search(variant["pattern"], txt):
                        present.append((variant["label"], loc))
                        break
            if len(present) >= 2:
                labels = " / ".join(p[0] for p in present)
                add(present[1][1], "SAME_PAGE_INCONSISTENCY", labels, f"{group['desc']}（同页出现 {labels}）", page_blob[:120])

    for (kind, num), locs in caption_hits.items():
        uniq = list(dict.fromkeys(locs))
        if len(uniq) >= 2:
            add(uniq[1], "CROSSREF_NUMBERING", f"{kind}{num}", f"{kind}号重复（{kind}{num} 出现 {len(uniq)} 次：{', '.join(uniq[:4])}），核对顺延编号", "")

    # Two sequence shapes: hyphenated `图3-2` (major-minor) and flat `图1..图5`.
    # The flat shape previously produced nothing because only len(parts)==2 was accepted.
    seq: dict[tuple[str, str], set[int]] = {}
    seq_loc: dict[tuple[str, str], str] = {}
    for (kind, num), locs in caption_hits.items():
        parts = num.split("-")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            axis = (kind, parts[0])
            seq.setdefault(axis, set()).add(int(parts[1]))
            seq_loc.setdefault(axis, locs[0])
        elif len(parts) == 1 and parts[0].isdigit():
            axis = (kind, "")
            seq.setdefault(axis, set()).add(int(parts[0]))
            seq_loc.setdefault(axis, locs[0])
    for (kind, major), minors in seq.items():
        if len(minors) >= 4:
            missing = [n for n in range(min(minors), max(minors) + 1) if n not in minors]
            if missing:
                sep = "-" if major else ""
                labels = "、".join(f"{kind}{major}{sep}{n}" for n in missing[:6])
                add(seq_loc[(kind, major)], "NUMBERING_GAP", f"{kind}{major}{sep}*", f"{kind}{major}{sep} 系列疑缺号：{labels}", "")

    if run_l2:
        for group in rules["cross_page_synonyms"]:
            found_variants: list[tuple[str, list[str]]] = []
            for variant in group["variants"]:
                locs_for_var: list[str] = []
                for loc, txt in units:
                    if re.search(variant["pattern"], txt):
                        locs_for_var.append(loc)
                if locs_for_var:
                    found_variants.append((variant["label"], locs_for_var))
            if len(found_variants) >= 2:
                summary_parts = [f"{lbl}({len(ls)}处)" for lbl, ls in found_variants]
                first_loc = found_variants[0][1][0]
                add(first_loc, "CROSS_PAGE_TERM_DRIFT", " vs ".join(summary_parts), f"{group['desc']}：{group['fix']}", " | ".join(summary_parts))

    if tables:
        findings.extend(_table_findings(tables))

    return findings


def strip_internal_fields(findings: list[dict]) -> list[dict]:
    return [{k: v for k, v in f.items() if not k.startswith("_")} for f in findings]


def build_chunks(units: list[tuple[str, str]], chunk_size: int) -> list[list[tuple[str, str]]]:
    if chunk_size <= 0 or not units:
        return [units] if units else []
    return [units[i:i + chunk_size] for i in range(0, len(units), chunk_size)]


def build_summary(loaded: dict, batch_size: int = 20) -> dict:
    batches: list[str] = []
    if loaded.get("format") == "pdf" and loaded.get("total", 0) > 0:
        total_p = int(loaded["total"])
        for start in range(1, total_p + 1, batch_size):
            batches.append(f"{start}-{min(start + batch_size - 1, total_p)}")
    return {
        "source": loaded.get("source", ""),
        "format": loaded.get("format", ""),
        "doc_type": loaded.get("doc_type", ""),
        "office_engine": loaded.get("office_engine", ""),
        "total_units": loaded.get("total", 0),
        "scanned_units": loaded.get("scanned", 0),
        # `total`/`scanned` count containers (PDF pages, pptx slides, xlsx sheets), not
        # audited paragraphs/cells. Report both so a 23-slide deck is not mistaken for a
        # 23-line audit — silent under-coverage was the failure mode here.
        "text_unit_count": len(loaded.get("units", [])),
        "low_text_pages": loaded.get("low_text_pages", []),
        "uncached_formula_cells": loaded.get("uncached_formula_cells", []),
        "recommended_page_batches": batches,
    }


def format_report_md(loaded: dict, findings: list[dict], profile: str, with_iec: bool) -> str:
    high = [f for f in findings if f["severity"] == "HIGH"]
    med = [f for f in findings if f["severity"] != "HIGH"]
    mode_tag = f"{profile}{'+IEC' if with_iec else ''}"
    lines = [
        f"### Coverage Ledger (`{mode_tag}`)",
        "| Containers (pages/slides/sheets) | Text units audited | Visual Pages (<50 chars) | HIGH hits | MEDIUM hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| {loaded['total']} | {len(loaded.get('units', []))} | {loaded['low_text_pages']} | {len(high)} | {len(med)} |",
        "",
        "### HIGH-Severity Findings (Verbatim, up to 60 rows)",
        "| Location | Category | Quoted Match | Suggested Fix |",
        "| :--- | :--- | :--- | :--- |",
    ]
    if high:
        for f in high[:60]:
            m_clean = f["match"].replace("|", "\\|")
            fix_clean = f["fix"].replace("|", "\\|")
            lines.append(f"| `{f['location']}` | `{f['category']}` | `{m_clean}` | {fix_clean} |")
        if len(high) > 60:
            lines.append(f"\n> Truncated HIGH rows: showing 60 of {len(high)} findings; inspect with `--chunk-size` / `--chunk-index`.")
    else:
        lines.append("| — | — | None | — |")

    lines.extend([
        "",
        "### MEDIUM-Severity Findings (Aggregated by Pattern)",
        "| Category | Match | Fix | Count | Sample Locations (max 5) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    if med:
        grouped: dict[tuple[str, str, str], list[str]] = {}
        for f in med:
            grouped.setdefault((f["category"], f["match"], f["fix"]), []).append(f["location"])
        ordered = sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0][0], kv[0][1]))
        for (cat, match, fix), locs in ordered:
            sample = ", ".join(dict.fromkeys(locs[:5]))
            m_clean = match.replace("|", "\\|")
            fix_clean = fix.replace("|", "\\|")
            lines.append(f"| `{cat}` | `{m_clean}` | {fix_clean} | {len(locs)} | `{sample}` |")
    else:
        lines.append("| — | None | — | 0 | — |")
    return "\n".join(lines)


CLAUSE_PAREN_RE = re.compile(r"\s*\((?:IEC|GB/T|Cl\.|Annex|ISO/IEC)[^)]*\)\s*$", re.IGNORECASE)


def _strip_clause_notes(text: str) -> str:
    cur = text.strip()
    while True:
        nxt = CLAUSE_PAREN_RE.sub("", cur).strip()
        if nxt == cur:
            return cur
        cur = nxt


def clean_pdf_replacement(match: str, category: str, fix: str) -> str:
    if category == "UNRESOLVED_SLOT":
        return "补填数据表核实值"
    if category == "COMPETITOR_CODE":
        if "contact" in match.lower():
            m_code = re.match(r"([A-Z]{2,4})\b", fix)
            if m_code:
                return f"{m_code.group(1)} contact"
        m_code = re.match(r"\(?([A-Z]{2,4})\)?", fix)
        if m_code:
            code = m_code.group(1)
            return f"({code})" if match.startswith("(") and match.endswith(")") else code
        return fix
    if category == "EN_SEVERE_ERROR" and fix == "plain integer operating cycles":
        return "<整数> operating cycles"
    return _strip_clause_notes(fix)


def _coalesce_high_compounds(findings: list[dict]) -> list[dict]:
    by_loc: dict[str, list[int]] = {}
    for idx, f in enumerate(findings):
        if f["severity"] == "HIGH":
            by_loc.setdefault(f["location"], []).append(idx)

    absorbed: set[int] = set()
    overrides: dict[int, str] = {}
    for idxs in by_loc.values():
        bl_idxs = [i for i in idxs if findings[i]["category"] == "EN_SEVERE_ERROR"]
        comp_idxs = [i for i in idxs if findings[i]["category"] == "COMPETITOR_CODE"]
        if not bl_idxs or not comp_idxs:
            continue
        for bi in bl_idxs:
            bf = findings[bi]
            m_bl_code = re.search(r"\(([A-Z]{2,4})\)", bf["fix"])
            if not m_bl_code:
                continue
            bl_code = m_bl_code.group(1)
            full_line = bf.get("_full_line") or bf.get("excerpt", "")
            for ci in comp_idxs:
                if ci in absorbed:
                    continue
                cf = findings[ci]
                m_c_code = re.match(r"\(?([A-Z]{2,4})\)?", cf["fix"])
                if not m_c_code or m_c_code.group(1) != bl_code:
                    continue
                cm = cf["match"]
                pat = rf"{re.escape(bf['match'])}\s*{re.escape(cm)}" if (cm.startswith("(") and cm.endswith(")")) else rf"{re.escape(bf['match'])}\s*\(\s*{re.escape(cm)}\s*\)"
                m_compound = re.search(pat, full_line)
                if m_compound:
                    overrides[bi] = m_compound.group(0)
                    absorbed.add(ci)
                    break

    out: list[dict] = []
    for idx, f in enumerate(findings):
        if idx in absorbed:
            continue
        if idx in overrides:
            nf = dict(f)
            nf["match"] = overrides[idx]
            out.append(nf)
        else:
            out.append(f)
    return out


ADVISORY_CATS = {"NUMERIC_RANGE", "BRACKET_UNBALANCED", "NUMBERING_GAP"}


def _replace_comment(rep: str, cat: str) -> str:
    if cat in ADVISORY_CATS or "不得" in rep or rep.startswith(("核", "修正", "删除", "补填")):
        return f"核查：{rep}"
    return f"替换为：{rep}"


def build_annotate_payload(findings: list[dict], author: str = "CHINT Catalog Edit", min_severity: str = "high") -> dict:
    findings = _coalesce_high_compounds(findings)
    high_seen: set[tuple[int, str, str]] = set()
    med_groups: dict[tuple[int, str, str], list[dict]] = {}
    items: list[dict] = []
    skipped_non_pdf = 0

    for f in findings:
        m = re.match(r"^P(\d+):", f["location"])
        if not m:
            if f["severity"] == "HIGH" or min_severity == "all":
                skipped_non_pdf += 1
            continue
        pno = int(m.group(1))
        if f["severity"] == "HIGH":
            search_str = f["match"].split(" + ")[0] if f["category"] == "TECH_HARD_ERROR" else f["match"]
            key = (pno, search_str.lower(), f["fix"])
            if key in high_seen:
                continue
            high_seen.add(key)
            rep = clean_pdf_replacement(search_str, f["category"], f["fix"])
            items.append({
                "page": pno,
                "search": search_str,
                "match_mode": "all",
                "comment": _replace_comment(rep, f["category"]),
                "author": author,
            })
        elif min_severity == "all":
            gkey = (pno, f["category"], f["fix"])
            med_groups.setdefault(gkey, []).append(f)

    if skipped_non_pdf:
        print(f"WARNING: skipped {skipped_non_pdf} non-PDF finding(s) lacking 'P{{n}}:' coordinates.", file=sys.stderr)

    for (pno, cat, fix), grp in med_groups.items():
        unique_matches = list(dict.fromkeys(f["match"] for f in grp))
        count = len(grp)
        rep = clean_pdf_replacement(unique_matches[0], cat, fix)
        base = _replace_comment(rep, cat)
        comment = base if count == 1 else f"{base}（本页共 {count} 处）"
        entry: dict = {"page": pno, "match_mode": "merged", "comment": comment, "author": author}
        if len(unique_matches) == 1:
            entry["search"] = unique_matches[0]
        else:
            entry["searches"] = unique_matches
        items.append(entry)

    items.sort(key=lambda x: (x["page"], 0 if x["match_mode"] == "all" else 1))
    return {"schema": "chint-office-annotate/v1", "annotations": items}


def emit_annotate_payload(findings: list[dict], out_target: str | Path, author: str = "CHINT Catalog Edit", min_severity: str = "high", extra_items: list[dict] | None = None) -> int:
    payload = build_annotate_payload(findings, author=author, min_severity=min_severity)
    if extra_items:
        payload["annotations"].extend(extra_items)
        payload["annotations"].sort(key=lambda x: (int(x["page"]), 0 if str(x.get("match_mode", "all")) == "all" else 1))
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if str(out_target) == "-":
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
    else:
        p = Path(out_target)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return len(payload["annotations"])


def run_self_test() -> int:
    import tempfile

    # 1. Parity anti-drift check — only against a sibling that is part of the same checkout.
    # A standalone install (or a machine holding an older deployed copy under
    # ~/.skills-manager) has every right to be out of step with this repo; failing the
    # self-test there would report a packaging bug that does not exist. The repo-wide
    # `scripts/verify_doc_skills.py` gate 2 is the place that asserts same-repo parity.
    trn_dir = resolve_translation_skill()
    ssot_live, ssot_src, _ = load_translation_ssot(trn_dir)
    same_checkout = (
        trn_dir is not None
        and Path(__file__).resolve().parent.parent.parent / "chint-translation" == trn_dir
    )
    if same_checkout:
        assert ssot_src == "sibling:chint-translation"
        for key in ("BLACKLIST_COMMON", "BLACKLIST_ACB", "BLACKLIST_MCCB", "COMPETITOR_RULES_COMMON", "COMPETITOR_RULES_ACB", "STD_CONCEPT_ZH", "STD_STATUTORY_ZH", "ED5_GUARD_TAGS"):
            assert ssot_live[key] == BUILTIN_SSOT_FALLBACK[key], f"SSOT drift detected on {key}!"
        assert ssot_live["ED5_CLAUSE_RE"].pattern == BUILTIN_SSOT_FALLBACK["ED5_CLAUSE_RE"].pattern

    # 2. Pure solo-mode test (office_dir=None, translation_dir=None) on synthetic PDF & DOCX
    fitz = _import_fitz()
    ssot_solo, solo_src, solo_path = load_translation_ssot(None)
    assert solo_src == "builtin-standalone" and solo_path is None

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        pdf_p = tdir / "solo_sample.pdf"
        doc = fitz.open()
        doc.new_page()  # P1 visual-only (<50 chars)
        p2 = doc.new_page()
        p2.insert_text((50, 60), "Ui(kV) 1000, Uimp(V) 8, 50KA, 2000m.")
        p2.insert_text((50, 90), "Closed electromagnet (XF) and Shunt Trip (MX).")
        doc.save(str(pdf_p))
        doc.close()

        loaded_pdf = load_units(str(pdf_p), office_dir=None)
        assert loaded_pdf["office_engine"] == "builtin-standalone"
        assert loaded_pdf["low_text_pages"] == [1], loaded_pdf
        res_solo_en = scan_units(loaded_pdf["units"], profile="L1", mode="en", dept="acb", ssot=ssot_solo)
        matches_en = {f["match"] for f in res_solo_en}
        assert {"Ui(kV)", "Uimp(V)", "XF", "MX"} <= matches_en, matches_en
        assert not any(m in matches_en for m in ("50KA", "2000m")), matches_en
        # Peer-validated legacy forms are L2 terminology consistency, not L1 hard errors.
        assert not {"Closed electromagnet", "Shunt Trip"} & matches_en, matches_en
        res_l2_en = scan_units(loaded_pdf["units"], profile="L2", mode="en", dept="acb", ssot=ssot_solo)
        assert {"Closed electromagnet", "Shunt Trip"} <= {f["match"] for f in res_l2_en}, res_l2_en
        assert all(f["severity"] == "MEDIUM" for f in res_l2_en if f["match"] in {"Closed electromagnet", "Shunt Trip"})

        # Built-in non-destructive PDF annotation writer in solo mode
        ann_payload = build_annotate_payload(res_solo_en)
        out_pdf = tdir / "solo_sample_annotated.pdf"
        ann_sum = write_annotated_pdf(pdf_p, ann_payload["annotations"], out_pdf, office_dir=None)
        assert ann_sum["office_engine"] == "builtin-standalone" and ann_sum["matched_items"] >= 2, ann_sum
        with fitz.open(str(pdf_p)) as sdoc, fitz.open(str(out_pdf)) as ddoc:
            assert len(list(sdoc[1].annots())) == 0, "Source PDF must remain untouched!"
            assert len(list(ddoc[1].annots())) >= 2, "Output PDF missing highlight annotations!"

        # Built-in word-boundary & wrapped-phrase PDF parity test
        wb_pdf = tdir / "wb_wrap.pdf"
        wb_doc = fitz.open()
        wb_p1 = wb_doc.new_page()
        wb_p1.insert_text((72, 100), "Column MN Omni autumn")
        wb_p1.insert_text((72, 125), "Rating 250A and 1250A")
        wb_p1.insert_text((72, 150), "Split line")
        wb_p1.insert_text((72, 165), "phrase")
        wb_doc.save(str(wb_pdf))
        wb_doc.close()
        wb_out = tdir / "wb_wrap_annotated.pdf"
        wb_items = [
            {"page": 1, "search": "MN", "match_mode": "all", "comment": "Code"},
            {"page": 1, "search": "250A", "match_mode": "all", "comment": "Exact token"},
            {"page": 1, "search": "Split line phrase", "match_mode": "all", "comment": "Wrapped"},
        ]
        wb_sum = write_annotated_pdf(wb_pdf, wb_items, wb_out, office_dir=None)
        assert wb_sum["office_engine"] == "builtin-standalone" and wb_sum["matched_items"] == 3 and wb_sum["highlight_annotations"] == 3, wb_sum
        with fitz.open(str(wb_out)) as wddoc:
            w_annots = [(a.type[1], len(a.vertices or [])) for a in wddoc[0].annots()]
            assert w_annots == [("Highlight", 4), ("Highlight", 4), ("Highlight", 8)], w_annots

        # Built-in DOCX extraction in solo mode
        docx_p = tdir / "solo_sample.docx"
        with zipfile.ZipFile(str(docx_p), "w") as zf:
            zf.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>海拨不超过2000m，涂润滑酯。</w:t></w:r></w:p></w:body></w:document>')
        loaded_docx = load_units(str(docx_p), office_dir=None)
        assert loaded_docx["office_engine"] == "builtin-standalone"
        res_docx = scan_units(loaded_docx["units"], profile="L1", mode="zh", ssot=ssot_solo)
        assert {"海拨", "润滑酯"} <= {f["match"] for f in res_docx}, res_docx

    # 3. Profile threshold calibration tests (L1 / L2 / L1+IEC / EN no-ortho)
    zh_units = [
        ("P36:L1", "瞬时电流 Ii 可设定范围：1.5In~50KA/65KA/75KA"),
        ("P36:L2", "□UVTZ 失压延时(详见 P036)"),
        ("P36:L3", "万能式断路器、闭合电磁铁、功率损耗、Inm=2000A、海拔不超过2000m、-5℃~+40℃。"),
        ("P44:L1", "额定绝缘电压 Ui(kV) 1000；额定冲击耐受电压 Uimp(V) 8；安装地点：海拨不超过2000m；涂润滑酯。"),
        ("P34:L1", "输入交流(AC220V)或直流(DC110V、"),
        ("P34:L2", "AC220V)电源。"),
        ("P32:L1", "6.10 透明保护罩（仅 NA1-2000X 抽屉式可提供），参见图：透明防护罩。"),
        ("P48:L1", "图 3"),
        ("P48:L2", "图 3"),
        ("P9:L1", "Sb1 分励按钮、其它、部分部份、订做。"),
    ]
    res_l1 = scan_units(zh_units, profile="L1", mode="zh", ssot=ssot_solo)
    for must_have in ("海拨", "润滑酯", "Ui(kV)", "Uimp(V)", "详见 P036", "图3"):
        assert any(must_have in f["match"] for f in res_l1), (must_have, res_l1)
    for must_suppress in ("50KA", "Sb1", "2000m", "℃", "万能式断路器", "闭合电磁铁", "功率损耗", "Inm", "部份", "订做", "其它"):
        assert not any(must_suppress in f["match"] for f in res_l1), (must_suppress, res_l1)

    res_l2 = scan_units(zh_units, profile="L2", mode="zh", ssot=ssot_solo)
    assert any("50KA" in f["match"] for f in res_l2) and any("Sb1" in f["match"] for f in res_l2)
    assert not any("2000m" in f["match"] or "℃" in f["match"] for f in res_l2)

    iec_units = [("P3:L1", "万能式断路器，使用类别 A，闭合电磁铁，结构差异，2000m，-5℃。")]
    res_iec = scan_units(iec_units, profile="L1", mode="zh", with_iec=True, dept="acb", ssot=ssot_solo)
    assert {"STD_CONCEPT_ERROR", "STD_STATUTORY_ZH"} <= {f["category"] for f in res_iec}
    assert not any("2000m" in f["match"] or "℃" in f["match"] for f in res_iec)

    # Category A + Isd (without vs with Icw), dept-aware closing magnet, and GB clause guard
    cat_a_no_icw = scan_units([("P10:L1", "Selectivity category: A"), ("P10:L2", "Short-time pick-up Isd = 6 Ir")], profile="L1", mode="en", dept="mccb", ssot=ssot_solo)
    cat_a_with_icw = scan_units([("P10:L1", "Selectivity category: A"), ("P10:L2", "Short-time pick-up Isd = 6 Ir; Icw = 5 kA")], profile="L1", mode="en", dept="mccb", ssot=ssot_solo)
    assert any(f["category"] == "TECH_HARD_ERROR" for f in cat_a_no_icw), cat_a_no_icw
    assert not any(f["category"] == "TECH_HARD_ERROR" for f in cat_a_with_icw), cat_a_with_icw

    cm_mccb = scan_units([("P11:L1", "Equipped with closing magnet.")], profile="L2", mode="en", dept="mccb", ssot=ssot_solo)
    cm_all = scan_units([("P11:L2", "Equipped with closing magnet.")], profile="L2", mode="en", dept="all", ssot=ssot_solo)
    assert len(cm_mccb) == 1 and cm_mccb[0]["fix"] == "Closing release", cm_mccb
    assert len(cm_all) == 1 and cm_all[0]["fix"] == "Closing release (CEM)", cm_all
    assert not scan_units([("P11:L1", "Equipped with closing magnet.")], profile="L1", mode="en", dept="all", ssot=ssot_solo)

    gb_guard_hits = scan_units([("P12:L1", "GB Cl. 4.3.6.2 applies.")], profile="L1", mode="en", with_iec=True, dept="all", ssot=ssot_solo)
    assert not any(f["category"] == "OBSOLETE_CLAUSE_ED5" for f in gb_guard_hits), gb_guard_hits

    ac22_hits = scan_units([("P13:L1", "使用类别 AC-22 额定电流；漏电互感器。")], profile="L1", mode="zh", with_iec=True, dept="all", ssot=ssot_solo)
    assert not any(f["category"] == "STD_CONCEPT_ERROR" for f in ac22_hits), ac22_hits
    assert any(f["match"] == "漏电互感器" and "电流传感器" in f["fix"] for f in ac22_hits), ac22_hits

    en_inm_hits = scan_units([("P14:L1", "Inm=250A")], profile="L1", mode="en", with_iec=True, dept="all", ssot=ssot_solo)
    assert not any(f["category"] == "STD_STATUTORY_ZH" for f in en_inm_hits), en_inm_hits

    # 4. Generic algorithm layer — sample deliberately uses words absent from catalog_rules.json
    assert load_catalog_rules()["version"], "catalog_rules.json not loaded"
    generic = scan_units([
        ("P1:L1", "额定电流范围 63~32A；Ics=65kA，Icu=50kA；断路器断路器。"),
        ("P1:L2", "另一区间 4000~4000；多出括号 ) 收尾。"),
        ("P1:L3", "图 4-1 外形一"),
        ("P1:L4", "图 4-2 外形二"),
        ("P1:L5", "图 4-3 外形三"),
        ("P1:L6", "图 4-5 外形五"),
        ("P2:L1", "图 3-2 抽屉式断路器外形"),
        ("P2:L2", "详见 P999"),
        ("P4:L1", "图 3-2 抽屉式断路器外形"),
    ], profile="L1", mode="zh", ssot=ssot_solo, total_pages=20)
    generic_cats = {f["category"] for f in generic}
    assert {"NUMERIC_RANGE", "TECH_HARD_ERROR", "DUPLICATE_WORD", "BRACKET_UNBALANCED", "CROSSREF_NUMBERING", "NUMBERING_GAP"} <= generic_cats, generic
    assert sum(1 for f in generic if f["category"] == "NUMERIC_RANGE") >= 2, generic

    clean_generic = scan_units([("P5:L1", "额定电流 16~63A；Icu=50kA，Ics=50kA。")], profile="L1", mode="zh", ssot=ssot_solo, total_pages=10)
    assert not clean_generic, clean_generic

    # 5. Standard relation & notation layer (In≤Inm, Ue≤Ui, GB/T 15835 range style, cos φ, 一, competitor codes)
    relations = scan_units([
        ("P6:L1", "In=250A，Inm=160A；Ue=690V，Ui=500V。"),
        ("P6:L2", "额定电流 16-63A；脱扣范围 50~100%；功率因数 CosΦ = 0.85；范围 16 一 63A。"),
        ("P7:L1", "额定电流 16~63A；脱扣范围 50%~100%；功率因数 cos φ = 0.85；cos ϕ = 0.9；第一 2 项，一般 10 分钟。"),
    ], profile="L2", mode="zh", ssot=ssot_solo, total_pages=10)
    assert sum(1 for f in relations if f["category"] == "TECH_HARD_ERROR") == 2, relations
    notation = [f["match"] for f in relations if f["category"] == "SYMBOL_CASE_NOTATION"]
    assert any("16-63A" in m for m in notation) and any("50~100%" in m for m in notation), relations
    assert any("CosΦ" in m for m in notation) and any("一" in m for m in notation), relations
    assert not any(f["location"] == "P7:L1" for f in relations), relations

    chint_mention_peer = scan_units(
        [("P8:L1", "CHINT NXA16 compatible with Siemens Modbus; Shunt Trip (MX) and XF.")],
        profile="L1", mode="en", dept="acb", ssot=ssot_solo,
    )
    assert {"MX", "XF"} <= {f["match"] for f in chint_mention_peer if f["category"] == "COMPETITOR_CODE"}, chint_mention_peer
    ext_flag_suppressed = scan_units(
        [("P8:L2", "CHINT NXA16 with MX and XF.")],
        profile="L1", mode="en", dept="acb", ssot=ssot_solo, external_reference=True,
    )
    assert not any(f["category"] == "COMPETITOR_CODE" for f in ext_flag_suppressed), ext_flag_suppressed
    peer_auto_suppressed = scan_units(
        [("P8:L3", "ABB Emax2 ABB SACE ABB Tmax MX XF")],
        profile="L1", mode="en", dept="acb", ssot=ssot_solo,
    )
    assert not any(f["category"] == "COMPETITOR_CODE" for f in peer_auto_suppressed), peer_auto_suppressed

    # 9. Table-level detector: Ics > Icu across adjacent rows of a ruled table
    tbl_bad = {"page": 8, "index": 0, "rows": [["", "", "Icu", "380V", "", "40", ""], ["", "", "Ics", "380V", "", "65", ""]]}
    tbl_ok = {"page": 7, "index": 0, "rows": [["", "", "Icu", "380V", "", "42", ""], ["", "", "Ics", "380V", "", "42", ""]]}
    tbl_far = {"page": 9, "index": 0, "rows": [["", "", "Icu", "380V", "", "20", ""], ["Iu", "", "", "", "", "2000", ""], ["", "", "Ics", "380V", "", "65", ""]]}
    assert len(_table_findings([tbl_bad])) == 1, _table_findings([tbl_bad])
    assert _table_findings([tbl_ok]) == [], _table_findings([tbl_ok])
    assert _table_findings([tbl_far]) == [], _table_findings([tbl_far])

    # 10. Regression guards for the defects found in the 2026-11 audit
    assert scan_units([("P1:L1", "In 800 A ratings, Inm = 630 A.")], profile="L1", mode="en", ssot=ssot_solo) == [], "EN preposition"
    assert scan_units([("P1:L1", "IEC 60947-2 applies.")], profile="L1", mode="en", ssot=ssot_solo, total_pages=50) == [], "std number"
    assert scan_units([("P1:L1", "G NXA16S12-AF3-AC220/230/240-3P+N (RF)")], profile="L1", mode="zh", ssot=ssot_solo) == [], "model code"
    assert any(f["category"] == "NUMERIC_RANGE" for f in scan_units([("P1:L1", "额定电流 100-63A")], profile="L1", mode="zh", ssot=ssot_solo)), "hyphen inversion"
    assert any(f["category"] == "NUMERIC_RANGE" for f in scan_units([("P1:L1", "6300~250A")], profile="L1", mode="zh", ssot=ssot_solo)), "wide inversion"
    assert any("左括号未闭合" in f["fix"] for f in scan_units([("P1:L1", "耐压 （100A")], profile="L1", mode="zh", ssot=ssot_solo)), "unclosed opener"
    assert scan_units([("P1:L1", "转矩 40 ～ 1.2In")], profile="L1", mode="zh", ssot=ssot_solo) == [], "relative multiple"
    assert scan_units([("P1:L1", "过载长延时延时时间可调")], profile="L1", mode="zh", ssot=ssot_solo) == [], "legit reduplication"
    assert any(f["category"] == "CROSSREF_NUMBERING" for f in scan_units([("P1:L1", "Fig. 1 view"), ("P2:L1", "Fig. 1 view")], profile="L1", mode="en", ssot=ssot_solo)), "EN caption dup"
    assert any(f["category"] == "NUMERIC_RANGE" for f in scan_units([("P1:L1", "12 500～20 000元")], profile="L1", mode="zh", ssot=ssot_solo)) is False, "grouped thousands"
    assert scan_units([("P1:L1", "地址必须在0x03~0x64之间")], profile="L1", mode="zh", ssot=ssot_solo) == [], "hex range"

    # 11. PPTX extraction (stdlib zip + DrawingML): numeric slide order, group-shape
    #     recursion, a:br line breaks, entity unescaping, notes excluded, blind signal.
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        pptx_p = tdir / "deck.pptx"

        def _slide(body: str) -> str:
            return (
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
                ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                f"<p:cSld><p:spTree>{body}</p:spTree></p:cSld></p:sld>"
            )

        def _sp(*paras: str) -> str:
            return "<p:sp><p:txBody><a:bodyPr/>" + "".join(f"<a:p>{p}</a:p>" for p in paras) + "</p:txBody></p:sp>"

        with zipfile.ZipFile(str(pptx_p), "w") as zf:
            zf.writestr("ppt/slides/slide2.xml", _slide(_sp("<a:r><a:t>Second</a:t></a:r>")))
            zf.writestr("ppt/slides/slide10.xml", _slide(_sp("<a:r><a:t>Tenth</a:t></a:r>")))
            zf.writestr("ppt/slides/slide1.xml", _slide(
                _sp("<a:r><a:t>A&amp;B</a:t></a:r><a:br/><a:r><a:t>C</a:t></a:r>")
                + f"<p:grpSp>{_sp('<a:r><a:t>Grouped</a:t></a:r>')}</p:grpSp>"
            ))
            zf.writestr("ppt/slides/slide3.xml", _slide(""))  # image-only slide
            zf.writestr("ppt/notesSlides/notesSlide1.xml", _slide(_sp("<a:r><a:t>NOT BODY TEXT</a:t></a:r>")))
        loaded_pptx = load_units(str(pptx_p), office_dir=None)
        assert loaded_pptx["format"] == "pptx" and loaded_pptx["doc_type"] == "office-generic", loaded_pptx
        assert loaded_pptx["total"] == 4 and loaded_pptx["low_text_pages"] == [3], loaded_pptx
        locs_pptx = [loc for loc, _ in loaded_pptx["units"]]
        assert locs_pptx == ["S1:T1:P1", "S1:T2:P1", "S2:T1:P1", "S10:T1:P1"], locs_pptx
        texts_pptx = dict(loaded_pptx["units"])
        assert texts_pptx["S1:T1:P1"] == "A&B\nC", texts_pptx  # entity unescaped, a:br -> newline
        assert texts_pptx["S1:T2:P1"] == "Grouped", texts_pptx  # inside <p:grpSp>
        assert not any("NOT BODY TEXT" in t for t in texts_pptx.values()), "notes slide leaked into body"
        assert not _PAGE_LOC_RE.match(locs_pptx[0]), "pptx locators must stay document-scoped"
        deck = tdir / "blind.pptx"
        with zipfile.ZipFile(str(deck), "w") as zf:
            zf.writestr("ppt/slides/slide1.xml", _slide(_sp("<a:r><a:t> </a:t></a:r>")))
            zf.writestr("ppt/slides/slide2.xml", _slide(""))
        blind = load_units(str(deck), office_dir=None)
        assert blind["units"] == [] and blind["low_text_pages"] == [1, 2], blind
        assert bool(blind["low_text_pages"]) and len(blind["low_text_pages"]) >= blind["total"], "blind guard would not fire"

        # 12. Markdown: fences and inline code are not prose; locators stay traceable
        md_p = tdir / "doc.md"
        md_p.write_text(
            "# 标题 海拨\n\n"
            "正文海拨错误，行内 `海拨` 不查，链接 `https://x/海拨` 不查。\n\n"
            "```\n海拨围栏内\n```\n\n"
            "~~~text\n海拨波浪围栏内\n~~~\n\n"
            "结尾海拨。\n",
            encoding="utf-8",
        )
        loaded_md = load_units(str(md_p), office_dir=None)
        assert loaded_md["format"] == "md" and loaded_md["doc_type"] == "markdown", loaded_md
        assert [loc for loc, _ in loaded_md["units"]] == ["M1", "M3", "M13"], loaded_md["units"]
        assert loaded_md["low_text_pages"] == [], "plain text has no pages to blind-guard"
        md_hits = scan_units(loaded_md["units"], profile="L1", mode="zh", ssot=ssot_solo)
        # Exactly the three prose occurrences: fenced and inline-code 海拨 never reach the scanner.
        assert len([f for f in md_hits if f["match"] == "海拨"]) == 3, md_hits
        fenced_p = tdir / "all_fenced.md"
        fenced_p.write_text("```\n海拨\n```\n", encoding="utf-8")
        loaded_fenced = load_units(str(fenced_p), office_dir=None)
        assert loaded_fenced["units"] == [] and loaded_fenced["low_text_pages"] == [], loaded_fenced
        txt_p = tdir / "plain.txt"
        txt_p.write_text("海拨\n", encoding="utf-8")
        loaded_txt = load_units(str(txt_p), office_dir=None)
        assert loaded_txt["doc_type"] == "text" and loaded_txt["units"] == [("Line 1", "海拨")], loaded_txt

        # 13. Legacy OLE2 (.doc/.xls): piece table, BIFF8 SST across CONTINUE, no silent empty
        assert _u32(b"\x01\x02\x03\x04", 0) == 0x04030201
        try:
            _ole2_streams(b"x" * 400)
            raise AssertionError("corrupt OLE2 must raise")
        except ValueError as exc:
            assert "OLE2" in str(exc), exc
        wd = bytearray(0x600)
        wd[0:2] = (0xA5EC).to_bytes(2, "little")
        wd[2:4] = (0xC1).to_bytes(2, "little")
        wd[0x0A:0x0C] = (0x0200).to_bytes(2, "little")
        utf16_text, narrow_text = "第一段", " Second"
        wd[0x400:0x400 + len(utf16_text) * 2] = utf16_text.encode("utf-16le")
        wd[0x500:0x500 + len(narrow_text)] = narrow_text.encode("cp1252")
        ccp = len(utf16_text) + len(narrow_text)
        wd[0x4C:0x50] = ccp.to_bytes(4, "little")
        wd[0x18:0x1C] = (0x400).to_bytes(4, "little")
        plc = (
            (0).to_bytes(4, "little")
            + len(utf16_text).to_bytes(4, "little")
            + ccp.to_bytes(4, "little")
            # PCD is 8 bytes: 2 flag bytes + 4-byte fc + 2-byte prm.
            + b"\x00\x00" + (0x400).to_bytes(4, "little") + b"\x00\x00"            # uncompressed piece
            + b"\x00\x00" + (0x40000000 | 0x500 * 2).to_bytes(4, "little") + b"\x00\x00"  # compressed piece
        )
        clx = b"\x02" + len(plc).to_bytes(4, "little") + plc
        wd[0x1A2:0x1A6] = (0).to_bytes(4, "little")
        wd[0x1A6:0x1AA] = len(clx).to_bytes(4, "little")
        assert _doc_piece_text(bytes(wd), clx) == "第一段 Second"
        doc_streams = {"WordDocument": bytes(wd), "1Table": clx}
        assert _extract_doc_units(doc_streams) == ["第一段 Second"], _extract_doc_units(doc_streams)
        raw_run = "回退文本".encode("utf-16le")
        assert _doc_raw_scan(raw_run, 4) == "回退文本"
        try:
            _extract_doc_units({"WordDocument": b"\x00" * 0x200})
            raise AssertionError("empty/corrupt WordDocument must raise")
        except ValueError as exc:
            assert ".doc" not in str(exc), exc  # the caller wraps with the actionable message

        # SST "ABC" split mid-UTF-16 across a CONTINUE boundary: the tail chunk opens with a
        # fresh fHighByte flag byte, which is the part naive parsers get wrong.
        abc = "ABC".encode("utf-16le")
        sst_atom = (
            (2).to_bytes(4, "little") + (2).to_bytes(4, "little")
            + (3).to_bytes(2, "little") + b"\x01" + abc[:4]
        )
        sst_cont = b"\x01" + abc[4:] + (2).to_bytes(2, "little") + b"\x00" + b"CD"
        assert _biff_sst([sst_atom, sst_cont]) == ["ABC", "CD"], _biff_sst([sst_atom, sst_cont])
        assert _xls_rk((123 << 2) | 0x02) == 123.0 and _xls_rk((12345 << 2) | 0x03) == 123.45

        def _rec(rid: int, payload: bytes) -> bytes:
            return rid.to_bytes(2, "little") + len(payload).to_bytes(2, "little") + payload

        bof = _rec(0x0809, (0x0600).to_bytes(2, "little") + b"\x00" * 14)
        sst_payload = (
            (3).to_bytes(4, "little") + (3).to_bytes(4, "little")
            + b"".join(len(s).to_bytes(2, "little") + b"\x00" + s.encode("cp1252") for s in ("S1", "S2", "S3"))
        )
        globals_recs = bof + _rec(0x00FC, sst_payload) + b"\x00" * 0  # placeholder
        sheet_name = "Sheet1"
        boundsheet = _rec(0x0085, b"\x00" * 4 + b"\x00\x00" + bytes([len(sheet_name), 0]) + sheet_name.encode("cp1252"))
        sheet_start = len(bof) + len(_rec(0x00FC, sst_payload)) + len(boundsheet)
        boundsheet = _rec(0x0085, sheet_start.to_bytes(4, "little") + b"\x00\x00" + bytes([len(sheet_name), 0]) + sheet_name.encode("cp1252"))
        sheet_body = (
            bof
            + _rec(0x00FD, (0).to_bytes(2, "little") + (0).to_bytes(2, "little") + b"\x00\x00" + (1).to_bytes(4, "little"))
            + _rec(0x0203, (0).to_bytes(2, "little") + (1).to_bytes(2, "little") + b"\x00\x00" + struct.pack("<d", 3.5))
            + _rec(0x027E, (1).to_bytes(2, "little") + (0).to_bytes(2, "little") + b"\x00\x00" + ((42 << 2) | 0x02).to_bytes(4, "little"))
            + _rec(0x00BD, (1).to_bytes(2, "little") + (1).to_bytes(2, "little")
                   + b"\x00\x00" + ((7 << 2) | 0x02).to_bytes(4, "little") + (1).to_bytes(2, "little"))
            + _rec(0x0006, (2).to_bytes(2, "little") + (0).to_bytes(2, "little") + b"\x00\x00"
                   + struct.pack("<d", 0) + b"\xff\xff\x00\x00" + b"\x00" * 4 + b"\x00\x00")
        )
        xls_streams = {"Workbook": bof + _rec(0x00FC, sst_payload) + boundsheet + sheet_body}
        xls_units = _extract_xls_units(xls_streams)
        assert xls_units == [
            {"location": "XSheet1:R1", "text": "S2 | 3.5"},
            {"location": "XSheet1:R2", "text": "42 | 7"},
            {"location": "XSheet1:R3", "text": "0"},
        ], xls_units
        try:
            _extract_xls_units({"Workbook": bof + boundsheet})
            raise AssertionError("sheet with no cell text must raise, not report 0 findings")
        except ValueError as exc:
            assert "未提取到任何单元格文本" in str(exc), exc
        corrupt_doc = tdir / "corrupt.doc"
        corrupt_doc.write_bytes(b"not an ole2 file" * 12)
        try:
            load_units(str(corrupt_doc), office_dir=None)
            raise AssertionError("corrupt .doc must raise")
        except ValueError as exc:
            assert "无法解析 .doc" in str(exc) and ".docx" in str(exc), exc

        lfs_doc = tdir / "lfs_pointer.doc"
        lfs_doc.write_text(
            "version https://git-lfs.github.com/spec/v1\noid sha256:0000000000000000\nsize 12345\n",
            encoding="utf-8",
        )
        try:
            load_units(str(lfs_doc), office_dir=None)
            raise AssertionError("Git LFS pointer must raise")
        except ValueError as exc:
            assert "Git LFS" in str(exc), exc

    print("SELF-TEST PASS: 13/13 suites passed (anti-drift/solo-PDF-write/solo-DOCX/L1-strict/L2-drift/L1+IEC/generic-layer/standard-relations/table-checks/defect-guards/pptx/markdown/legacy-ole2).")
    return 0


def main() -> int:
    _ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Standalone + sibling-aware CHINT catalogue audit & PDF annotation engine")
    parser.add_argument("source", nargs="?", help=".pdf/.docx/.xlsx/.pptx/.doc/.xls/.md/.txt, chint-office-extract/v1 JSON, or '-'")
    parser.add_argument("--profile", choices=["L1", "L2", "L3"], default="L1", help="Threshold profile (default: L1 strict errors only)")
    parser.add_argument("--with-iec", action="store_true", help="Overlay substantive GB/T 14048.2 & IEC 60947-2 checks onto L1/L2")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all", help="Product department scope (default: all)")
    parser.add_argument("--external-reference", action="store_true", help="Suppress CHINT-internal competitor accessory code checks when auditing a peer/external catalogue")
    parser.add_argument("--mode", choices=["auto", "zh", "en"], default="auto", help="Language mode (default: auto)")
    parser.add_argument("--pages", help="PDF page range, e.g. 1-20 or 1,3,5")
    parser.add_argument("--summary", action="store_true", help="Print compact document metadata & page batches without auditing")
    parser.add_argument("--office-dir", help="Optional path to sibling chint-office-suite (or /nonexistent to force built-in)")
    parser.add_argument("--translation-dir", help="Optional path to sibling chint-translation (or /nonexistent to force built-in)")
    parser.add_argument("--check-env", action="store_true", help="Check Python, optional pymupdf/openpyxl, and sibling skill availability")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--report-md", action="store_true", help="Output deduplicated Markdown report")
    parser.add_argument("--emit-annotate", help="Write chint-office-annotate/v1 JSON to '-' or file path")
    parser.add_argument("--write-pdf", help="Write non-destructive annotated copy of this PDF (uses sibling or built-in PyMuPDF)")
    parser.add_argument("--output", help="Output PDF path for --write-pdf (default: <stem>_annotated.pdf)")
    parser.add_argument("--extra-annotations", help="Optional extra chint-office-annotate/v1 JSON file or '-' merged into --write-pdf / --emit-annotate")
    parser.add_argument("--annotate-severity", choices=["high", "all"], default="high", help="Minimum severity for PDF annotations (default: high)")
    parser.add_argument("--author", default="CHINT Catalog Edit", help="Annotation author")
    parser.add_argument("--chunk-size", type=int, default=0, help="Split units into chunks of N non-empty lines")
    parser.add_argument("--chunk-index", type=int, default=0, help="Inspect 1-based chunk K only")
    parser.add_argument("--chunks-info", action="store_true", help="Print chunk manifest with per-chunk hit counts")
    parser.add_argument("--exit-zero", action="store_true", help="Exit 0 even when findings exist")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    try:
        if args.self_test:
            return run_self_test()
        if args.check_env:
            info = check_env(args.office_dir, args.translation_dir)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            return 0 if info["ready"] else 1
        if not args.source:
            parser.error("source is required unless --self-test or --check-env is set")

        off_dir = resolve_office_skill(args.office_dir)
        trn_dir = resolve_translation_skill(args.translation_dir)
        loaded = load_units(args.source, pages_spec=args.pages, office_dir=off_dir)
        if args.summary:
            summary = build_summary(loaded)
            print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else f"{summary['format']}/{summary['doc_type']} ({summary['office_engine']}) | total={summary['total_units']} | scanned={summary['scanned_units']} | low_text_pages={summary['low_text_pages']} | batches={summary['recommended_page_batches']}")
            return 0

        units = loaded["units"]
        eff_mode = detect_mode(units) if args.mode == "auto" else args.mode
        ssot, ssot_source, ssot_path = load_translation_ssot(trn_dir)

        if args.chunks_info:
            csize = args.chunk_size if args.chunk_size > 0 else 50
            chunks = build_chunks(units, csize)
            manifest_chunks = []
            for idx, ch in enumerate(chunks, 1):
                cf = scan_units(ch, profile=args.profile, mode=eff_mode, with_iec=args.with_iec, dept=args.dept, ssot=ssot, total_pages=loaded["total"] if loaded["format"] in {"pdf", "extract-json"} else None, external_reference=args.external_reference)
                manifest_chunks.append({
                    "index": idx,
                    "start_location": ch[0][0],
                    "end_location": ch[-1][0],
                    "unit_count": len(ch),
                    "high_hits": sum(1 for f in cf if f["severity"] == "HIGH"),
                    "medium_hits": sum(1 for f in cf if f["severity"] != "HIGH"),
                })
            manifest = {
                "source": loaded["source"],
                "doc_type": loaded.get("doc_type", ""),
                "profile": args.profile,
                "with_iec": args.with_iec,
                "mode": eff_mode,
                "office_engine": loaded["office_engine"],
                "ssot_source": ssot_source,
                "ssot_path": ssot_path,
                "rules_path": str(CATALOG_RULES_PATH),
                "total_units": len(units),
                "chunk_size": csize,
                "total_chunks": len(chunks),
                "low_text_pages": loaded["low_text_pages"],
                "chunks": manifest_chunks,
            }
            if args.json:
                print(json.dumps(manifest, ensure_ascii=False, indent=2))
            else:
                print(f"Total units: {manifest['total_units']} | Chunks: {manifest['total_chunks']} (size={csize}) | profile={args.profile} | ssot={ssot_source} | office={loaded['office_engine']} | low_text_pages={manifest['low_text_pages']}")
                for c in manifest_chunks:
                    print(f"  Chunk {c['index']}: {c['start_location']}..{c['end_location']} ({c['unit_count']} units) | HIGH={c['high_hits']} MEDIUM={c['medium_hits']}")
            return 0

        active_units = units
        chunk_meta = None
        chunk_range: tuple[int, int] | None = None
        # A run that extracted no text (image-only PDF) is not a clean pass.
        # A run that extracted no text (image-only PDF, empty Word/Excel, text-less deck) is
        # not a clean pass. PDF/pptx report emptiness through low_text_pages, but docx/xlsx
        # have no per-container signal, so an empty unit set has to be caught directly —
        # otherwise `findings=0` reads as a clean bill of health for a file never audited.
        _low = loaded.get("low_text_pages") or []
        audit_blind = (bool(_low) and len(_low) >= loaded.get("total", 0) and not units) or (
            not units and loaded.get("format") in {"docx", "xlsx", "xlsm"}
        )
        if args.chunk_index > 0:
            csize = args.chunk_size if args.chunk_size > 0 else 50
            chunks = build_chunks(units, csize)
            if args.chunk_index > len(chunks):
                raise ValueError(f"--chunk-index {args.chunk_index} out of range 1..{len(chunks)}")
            start = (args.chunk_index - 1) * csize
            chunk_range = (start, start + len(chunks[args.chunk_index - 1]))
            chunk_meta = {"index": args.chunk_index, "total_chunks": len(chunks), "unit_count": chunk_range[1] - chunk_range[0]}
            print(
                f"NOTE: chunk {args.chunk_index}/{len(chunks)} — the full document is scanned so "
                f"cross-page detectors stay correct; only findings inside this chunk are printed.",
                file=sys.stderr,
            )

        # Global detectors (cross-page term drift, caption duplicates, numbering gaps,
        # same-page conflicts, cumulative bracket balance) only work on the whole document.
        # Always scan the full unit set, then narrow the *output* to the requested chunk.
        findings = scan_units(units, profile=args.profile, mode=eff_mode, with_iec=args.with_iec, dept=args.dept, ssot=ssot, total_pages=loaded["total"] if loaded["format"] in {"pdf", "extract-json"} else None, tables=loaded.get("tables"), external_reference=args.external_reference)
        if chunk_range is not None:
            lo_i, hi_i = chunk_range
            in_chunk = {loc for loc, _ in units[lo_i:hi_i]}
            findings = [f for f in findings if f["location"] in in_chunk]

        extra_items: list[dict] = []
        if args.extra_annotations:
            raw_extra = sys.stdin.read() if args.extra_annotations == "-" else Path(args.extra_annotations).read_text(encoding="utf-8")
            extra_obj = json.loads(raw_extra)
            extra_list = extra_obj["annotations"] if isinstance(extra_obj, dict) else extra_obj
            if not isinstance(extra_list, list):
                raise ValueError("--extra-annotations must be a JSON list or an object with 'annotations'.")
            extra_items = extra_list

        if args.write_pdf:
            inp_pdf = Path(args.write_pdf)
            out_pdf = Path(args.output) if args.output else inp_pdf.with_name(f"{inp_pdf.stem}_annotated.pdf")
            payload = build_annotate_payload(findings, author=args.author, min_severity=args.annotate_severity)
            all_items = payload["annotations"] + extra_items
            all_items.sort(key=lambda x: (int(x["page"]), 0 if str(x.get("match_mode", "all")) == "all" else 1))
            summary = write_annotated_pdf(inp_pdf, all_items, out_pdf, default_author=args.author, office_dir=off_dir)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0

        if args.emit_annotate:
            emit_annotate_payload(findings, args.emit_annotate, author=args.author, min_severity=args.annotate_severity, extra_items=extra_items)
            if args.emit_annotate == "-":
                return 0

        clean_findings = strip_internal_fields(findings)
        report = {
            "source": loaded["source"],
            "format": loaded["format"],
            "doc_type": loaded.get("doc_type", ""),
            "office_engine": loaded["office_engine"],
            "profile": args.profile,
            "with_iec": args.with_iec,
            "dept": args.dept,
            "mode": eff_mode,
            "ssot_source": ssot_source,
            "ssot_path": ssot_path,
            "rules_path": str(CATALOG_RULES_PATH),
            "total_units": loaded["total"],
            "scanned_units": loaded["scanned"],
            "low_text_pages": loaded["low_text_pages"],
            "finding_count": len(clean_findings),
            "high_count": sum(1 for f in clean_findings if f["severity"] == "HIGH"),
            "medium_count": sum(1 for f in clean_findings if f["severity"] != "HIGH"),
            "findings": clean_findings,
        }
        if chunk_meta:
            report["chunk"] = chunk_meta
            report["units"] = [{"location": loc, "text": txt} for loc, txt in active_units]

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif args.report_md:
            print(format_report_md(loaded, clean_findings, args.profile, args.with_iec))
        else:
            print(f"[{args.profile}{'+IEC' if args.with_iec else ''}] Scanned {report['scanned_units']}/{report['total_units']} containers, {len(units)} text units | doc_type={report['doc_type']} | office={report['office_engine']} | ssot={ssot_source} | low_text_pages={report['low_text_pages']} | findings={report['finding_count']} (HIGH={report['high_count']}, MEDIUM={report['medium_count']})")
        if chunk_meta and not (args.json or args.report_md):
            print(f"--- Chunk {chunk_meta['index']}/{chunk_meta['total_chunks']} ({chunk_meta['unit_count']} units) ---")
            print("--- Findings ---")
        if not (args.json or args.report_md):
            for f in clean_findings:
                print(f"[{f['location']}] ({f['severity']}/{f['category']}) '{f['match']}' -> {f['fix']}")
        if audit_blind:
            if _low:
                why = (
                    f"{len(_low)} of {loaded['total']} page(s) carry no extractable text "
                    f"(image-only or vector art); those pages were never audited"
                )
            else:
                why = (
                    f"the {loaded.get('format', 'file')} yielded no extractable text at all — "
                    f"the content is likely image-only, or the file is empty"
                )
            print(
                f"BLIND PASS: {why}. findings=0 does NOT mean clean — inspect the source. "
                f"Convert to a text-bearing format or review the pages visually before signing off.",
                file=sys.stderr,
            )
            return 2
        return 0 if args.exit_zero else (1 if clean_findings else 0)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
