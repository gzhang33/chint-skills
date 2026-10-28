# Presentation Delivery and Save Troubleshooting (macOS / Windows)

Read this guide only when the user reports an opening, editing, or saving problem.
Choose the section for the affected operating system. Start with read-only checks and
record the exact error, application, version, and output location. Do not change access
permissions or security settings, terminate applications, or remove lock files without
the user's approval. OpenXML validation alone does not prove that a person can edit or
save a presentation in PowerPoint or WPS.

---

## 1. Protected View — the quarantine attribute

**Symptom.** The deck opens read-only with a yellow banner; edits cannot be saved.
**Cause.** `com.apple.quarantine` on the file. Office opens quarantined files in
Protected View, which is read-only until "启用编辑" is clicked.
**Trap.** PowerPoint **re-adds the attribute to files it opens/saves** (agent string
`Microsoft PowerPoint`), so a one-off `xattr -d` is not a permanent fix.

```bash
xattr -p com.apple.quarantine "deck.pptx"        # present? → Protected View risk
xattr -d com.apple.quarantine "deck.pptx"        # clear it
# control: files written by LibreOffice / python-pptx carry NO quarantine — the agent
# string tells you which application applied it.
```

**Durable fix (user-side, ask them to do it):** PowerPoint → 偏好设置 → 信任中心 →
**受信任位置** → add the working folder. The folder then never enters Protected View.

---

## 2. File occupancy — someone already holds the file

**Symptom.** "文件正在使用中" / opened read-only / saves silently lost.
**Cause.** A live PowerPoint (or WPS) instance holds the document, often a stale one
left behind by an earlier automation run; a `~$name.pptx` owner file persists after a
crash.

```bash
lsof "deck.pptx"                        # any FD open on it?
ls -la "$(dirname "deck.pptx")" | grep '~\$'   # stale Office owner file?
find . -name '~\$*.pptx'                # same, recursive
```

**Next step.** Confirm whether a person or Office process still has the file open. Ask
the user to close it if needed. Remove a `~$` owner file only after confirming that no
person or process is editing the presentation. **Do not edit a deck while another
instance has it open.**

---

## 3. External hard links — cloud-sync clients

**Symptom.** Edits vanish, or the file reverts after saving; multiple "copies" share one
inode.
**Cause.** File-provider / sync clients (Feishu/Lark/ChintOA, Dropbox, OneDrive) stage
hard links to synced files. A save that replaces the path leaves the staged links on the
old inode, and the client can push its staged version back over the user's edit.

```bash
stat -f "inode=%i links=%l" "deck.pptx"          # links > 1 → investigate
find ~ -inum "$(stat -f %i "deck.pptx")" 2>/dev/null   # scope it to avoid a full-disk scan
# typical hits: /private/var/folders/**/T/<vendor>_sync_*/…
```

**Next step.** Save a separate working copy to a user-approved location outside the
provider-managed folder, then confirm that copy opens and saves. Do not replace the
source file or break hard links automatically.

---

## 4. Stale package metadata — `docProps/app.xml`

**Symptom.** File → Info reports the wrong slide count; document properties contradict
the deck.
**Cause.** `<Slides>` / `<Notes>` are maintained by Office on save. A deck assembled by
python-pptx inherits the **source** deck's counters — a 23-page build reported
`<Slides>19</Slides>`.

```bash
unzip -p "deck.pptx" docProps/app.xml | grep -oE '<Slides>[0-9]+</Slides>|<Notes>[0-9]+</Notes>'
python3 -c "from pptx import Presentation; print(len(Presentation('deck.pptx').slides))"
```

`shell_rebuild_engine.py` repairs these counters after saving; check them anyway when a
deck was produced by other means.

---

## 5. Renderer auto-growth — XML says it fits, the render says otherwise

**Symptom.** A table's last row sits on the footer / decorative strip although every
geometry check passed.
**Cause.** `<a:tr h="…">` is a **minimum**. PowerPoint and LibreOffice grow rows to fit
their text (observed: a row whose XML height sum renders taller once the renderer
auto-grows it to fit text), so XML-only validation is
blind to it.

**Rule.** Any claim about bottom clearance, footer collision or table overflow must be
made on **rendered pixels**, never on XML geometry alone.

```bash
soffice --headless --convert-to pdf --outdir /tmp/render "deck.pptx"
pdftoppm -r 150 -png /tmp/render/deck.pdf /tmp/render/slide
# then measure the band: content pixels below the footer/strip line ⇒ real defect
```

Corollary for the footer policy: never "make room" by shrinking a row below its natural
text height — the renderer grows it back.

---

## 6. Rendering is not pixel-deterministic — compare structure, not pixels

The same file rendered twice by LibreOffice differed by a non-trivial share of pixels
(and the dark-pixel count moved even more). **Pixel equality is not a valid acceptance test.**

- Compare **structural** quantities: a table's bottom border row index, a rule's y, text
  bounding boxes.
- When auditing visually, run the vision model on a **read-only sandbox** and cross-check
  every claim against a deterministic check: the vision model misread CJK repeatedly in
  practice (it once reported a value ordering as wrong that was byte-identical to the
  source).

---

## 7. Automated saves are not evidence of editability

Driving PowerPoint by AppleScript, `save` / `save as` **report success while writing
nothing** — the bytes land in the app's own sandbox container
(`~/Library/Containers/com.microsoft.Powerpoint/Data/tmp/`). This reproduces with a
brand-new presentation PowerPoint itself created, so it says nothing about your file.

Consequences:

- Never use a scripted PowerPoint save as proof that a deck is editable.
- Prove writability with a non-Office writer instead:
  `python3 -c "from pptx import Presentation; p=Presentation(f); p.save(f)"`.
- Ask the user to confirm a real UI save, and if the report persists, get the **exact
  banner or error text** plus which application they used before theorising further.

---

## 8. Package-level read-only markers (rule these out early)

```bash
unzip -q "deck.pptx" -d /tmp/chk
grep -ril "modifyVerifier\|_MarkAsFinal\|writeProtection\|documentProtection" /tmp/chk
ls /tmp/chk/docProps/custom.xml /tmp/chk/_xmlsignatures 2>/dev/null   # absent = good
find /tmp/chk -type f -size 0                                          # empty part = corrupt
python3 scripts/office/validate.py "deck.pptx" --original "source.pptx"
```

Absence of these markers, plus a successfully parsed presentation, narrows the diagnosis
but does not prove that the file itself is not blocking edits or saves.

---

## 9. Windows: PowerPoint or WPS cannot edit or save

Keep the original file unchanged. Ask for the exact banner or error, the application and
version, the file location, and whether saving a new copy to another user-approved
location succeeds. PowerPoint menu names below are Microsoft-specific; record WPS's
actual message instead of assuming that it uses the same mechanism.

### Read-only or Protected View

Check the file's Windows Properties for the Read-only attribute. Files from the internet
or other untrusted locations can open in Protected View with editing disabled. If the
user trusts the file's source, they can choose **Enable Editing** in PowerPoint. Do not
recommend disabling Protected View, changing Trust Center policies, or editing registry
settings as a routine fix. Microsoft explains [Protected View](https://support.microsoft.com/en-us/office/collab-files/what-is-protected-view)
and [read-only presentations](https://support.microsoft.com/en-us/office/collab-files/why-did-my-file-open-read-only).

### File is locked or commands are unavailable

Check whether another person, device, or Office process has the presentation open. For a
shared file, a lock can be legitimate; Microsoft recommends saving a separate copy when
work must continue before the lock clears. Keep both copies and reconcile changes later.
Do not delete `~$` owner files or force-close Office processes until the user confirms
that no active editor owns the file. See Microsoft's [locked-file guidance](https://support.microsoft.com/en-us/office/collab-files/file-is-locked-by-another-user-and-commands-are-grayed-out).

### Save fails only at one location

Check that the user can create a separate file in the destination folder, that the drive
has free space, and that OneDrive or SharePoint sync has no reported error or quota
limit. Test **Save As** to a new name in a user-approved local folder. Do not change
folder permissions, disable security software or sync, or overwrite the source. Microsoft
lists storage and read-only causes in its [read-only troubleshooting](https://support.microsoft.com/en-us/office/collab-files/why-did-my-file-open-read-only).

### Confirm the result

Only report Windows save compatibility when the final file was opened and saved through
the actual Windows PowerPoint or WPS interface. Record the Windows and application
versions. If that environment is unavailable, report the Windows save check as unverified.

---

## Resolution evidence

Report the checks actually performed and their result. Distinguish package validation,
render inspection, and an interactive save in the affected application. Do not mark a
reported save failure resolved until the user confirms the saved copy opens and remains
editable in the target application.
