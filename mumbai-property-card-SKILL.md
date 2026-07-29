---
name: "mumbai-property-card"
description: "Manual command /mumbai-property-card — fetch the Property Card / PR Card (मालमत्ता पत्रक) for Mumbai City or Mumbai Suburban plots from MahaBhulekh, given CTS number(s) and village. Produces a lawyer-style title summary with a confidence score, and supports unattended batches. Run only when the user explicitly invokes /mumbai-property-card; do not auto-trigger."
user-invocable: true
disable-model-invocation: true
---

# /mumbai-property-card — PR Card lookup + title summary (MahaBhulekh)

Start at **§0 — ask Single or Batch, then confirm inputs.** Site
`https://bhulekh.mahabhumi.gov.in`, ASP.NET + UpdatePanel, no API.
Drive with `javascript_tool`; web_fetch/curl cannot post the form.
Per plot: **3 JS calls + 3 images**, ~30–60 s wall clock, **one captcha each** (cannot be
batched — see Gotchas). Never screenshot the form; the helpers return its state.

## 0. First — ask Single or Batch, then confirm inputs
On invocation, **ask via `AskUserQuestion`: Single PR Card or Batch?** — unless the request
already settles it (a lone CTS = single; a list = batch). Never ask twice, and never ask if
the user already gave village + numbers; just confirm the defaults in one line and run.

Then state what you need, in three tiers. Ask only for the **Required** ones; name the
Recommended and Optional so the user can volunteer them.

| Tier | Item | Why |
|---|---|---|
| **Required** | **Village** | CTS numbers repeat across villages; the wrong village returns a real card for the wrong plot with no error |
| **Required** | **CTS number(s)** | one for single; a list for batch |
| Recommended | City or Suburban | skips a guess; Byculla/Fort/Worli = City, Marol/Andheri/Bandra = Suburban |
| Recommended | CSO office (Suburban only) | saves a 10-office scan — boundaries don't follow suburb names |
| Recommended | Downloads connected + Chrome multi-download allowed | required for JPEGs; **must be set before a batch starts**, not mid-run |
| Optional | Mobile number | defaults `9821114112`; the site requires it but never verifies it |
| Optional | Sub-plot policy | default: fetch all (`100` and `100/1187`) |
| Optional | PU-ID, if known | **Suburban only** — skips the whole cascade |

**Worked example — Mumbai City**
> "Byculla: 1640"
> → district `23`, office `2301`, village `2301014100` (Byculla). Village names are English.
> Returns the English Survey Register. Nothing else needed.

**Worked example — Mumbai Suburban**
> "Marol (Vile Parle): 1590"
> → district `22`, office `2206`, village `मरोळ`. Village names are Marathi.
> Returns the Marathi मालमत्ता पत्रक, and prints `PU-ID: 87530537828` — record it, and
> re-fetching that plot later skips the cascade entirely.
> Without the office, expect one extra call to locate मरोळ (it is under Vile Parle, **not**
> Andheri).

For batch, restate the agreed policies and the time estimate (**30–60 s per plot**) before
starting, then run to completion without interrupting — see §7.

## Runtimes — bun and uv only
Any script run **locally in the sandbox** uses **`bun`** for JS/TS and **`uv`** for Python.
Never `node`, `npm`, `python3`, `pip` or `pip install --break-system-packages` directly.

    bun run x.ts · bun x <pkg>            # never node/npm
    uv run x.py · uv run --with pillow …  # never python3/pip
    uv pip install --system <pkg>          # only if a bare interpreter is unavoidable

Two honest limits, both verified in this sandbox:
- **The JavaScript in §1 is exempt** — it is evaluated inside the user's Chrome page by
  `javascript_tool`, not by any local runtime. Bun cannot execute in a page context, so
  this rule cannot apply to it. It stays browser JS.
- **`bun` is not installed and cannot be installed** (the proxy returns 403 for outbound
  installs; `uv` is present at 0.11.19 but also cannot reach PyPI). If a local JS script is
  ever genuinely needed, say bun is unavailable and ask — do not silently fall back to node.

## 1. Navigate, then paste once per page load

```javascript
prm=Sys.WebForms.PageRequestManager.getInstance();
lastAlert=null; window.alert=m=>{lastAlert=m};              // MUST precede any click
pb=(f,ms=45000)=>new Promise((y,n)=>{const h=()=>{prm.remove_endRequest(h);y()};
  prm.add_endRequest(h);setTimeout(()=>{prm.remove_endRequest(h);n('timeout')},ms);f()});
$=id=>document.getElementById('ContentPlaceHolder1_'+id);
dd=(id,v)=>pb(()=>{const e=$(id);e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}))});
crop=el=>{el.scrollIntoView({block:'center'});const r=el.getBoundingClientRect(),s=1340/innerWidth;
  return [Math.round(r.left*s)-6,Math.round(r.top*s)-6,Math.round(r.right*s)+6,Math.round(r.bottom*s)+6]};
// village postback re-renders txtcsno; a bare .value can land on the old node and vanish,
// which then reads as "invalid CTS". Always set-and-verify.
setCts=async v=>{for(let i=0;i<5;i++){const e=$('txtcsno');e.value=v;
  e.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,200)); if($('txtcsno').value===v) return true;} return false};

find=async(dist,off,vill,cts,mob='9821114112')=>{
  await pb(()=>$('rbtnSelectType_2').click());
  await dd('ddlMainDist',dist); await dd('ddlTalForAll',off); await dd('ddlVillForAll',vill);
  if(!await setCts(cts)) return {error:'field would not hold value'};
  lastAlert=null; await pb(()=>$('btnsearchfind').click());
  const o=[...$('ddlsurveyno').options].slice(1).map(x=>({v:x.value,t:x.text}));
  if(!o.length) return {notFound:lastAlert};
  if(o.length>1) return {choose:o.map(x=>x.t)};
  await dd('ddlsurveyno',o[0].v); $('txtmobile1').value=mob;
  return {ok:o[0].t, captcha:crop($('captchaImage'))};
};
submit=async(code,fname)=>{
  $('txtcaptcha').value=code; lastAlert=null;
  try{await pb(()=>$('btnmainsubmit').click())}catch(e){}
  const i=$('ImgPC'); if(!i) return {error:lastAlert||'no card'};
  const a=document.createElement('a');a.href=i.src;a.download=fname+'.jpg';
  document.body.appendChild(a);a.click();a.remove();
  i.style.width=(innerWidth-20)+'px'; i.style.height='auto';
  await new Promise(r=>setTimeout(r,300));
  const sc=$('showPopUp');
  return {bands:Math.ceil(sc.scrollHeight/(sc.clientHeight-60)), h:sc.scrollHeight, natural:i.naturalHeight};
};
// card sits in an inner scroller — window.scrollTo does NOT move it
band=async n=>{const sc=$('showPopUp'),i=$('ImgPC');
  sc.scrollTop=n*(sc.clientHeight-60); await new Promise(r=>setTimeout(r,250));
  const a=sc.getBoundingClientRect(),b=i.getBoundingClientRect(),s=1340/innerWidth;
  return {region:[Math.round(Math.max(a.left,b.left)*s),Math.round(Math.max(a.top,0)*s),
    Math.round(Math.min(a.right,b.right)*s),Math.round(Math.min(a.bottom,innerHeight)*s)],
    scrollTop:sc.scrollTop, atEnd:sc.scrollTop+sc.clientHeight>=sc.scrollHeight-5}};
```

## 2. Codes
**District** `23` मुंबई शहर · `22` मुंबई उपनगर. Select by **value**; display text is Marathi
with typos elsewhere on the site.

**City** → office `2301`; 24 villages, names in **English**.
**Suburban** → ten City Survey Offices: `2201` Borivali · `2202` Malad · `2203` Goregaon ·
`2204` Andheri · `2205` Bandra · `2206` Vile Parle · `2207` Ghatkopar · `2208` Chembur ·
`2209` Mulund · `2210` Kurla; village names in **Marathi** (मरोळ = Marol).

CSO boundaries don't follow suburb names — **Marol is under Vile Parle, not Andheri**. To
locate one, loop `await dd('ddlTalForAll',code)` and filter the village options, **five
offices per call** (ten exceeds the 45 s CDP limit). Read lists live; don't trust memory.

## 3. Captcha → submit
Zoom the `captcha` region, read it (**case-sensitive**: `vPVLRU`, `tO6tZ1`), then
`submit(code,'propcard_<village>_<cts>')`. It survives postbacks. On rejection click
`$('btnreferesh')` (site's misspelling; `ImageButton3` on the PU-ID panel), re-read, retry
×3, then show the user the crop. **Captcha failure is never evidence the plot is missing.**
Never re-click submit while waiting — it invalidates the captcha.

## 4. Not found — say so, don't dig
Two alerts both mean not found: `Please Enter Valid CTS.No... ...!` (City) and
`न.भु.क्र./CTS नंबर उपलब्ध नाही ...!` (Suburban; also City for an absent sub-plot form).
**Before concluding, run a control search on a number known to exist in that village**
(e.g. Byculla 1640). Control passes + target fails = the gap is real and the session is
healthy; say exactly that.

Report it plainly and stop. Do not blame the input, do not interrogate, do not scan other
villages uninvited — absence from the online register is frequently a **government record
or digitisation gap**, not a wrong entry. Offer in one line to try a variant or another
village. `{choose:[...]}` = sub-plots exist; follow the sub-plot policy (§7).

## 5. Read the card — verification protocol
The card is **one JPEG** (`#ImgPC`); no text layer, `get_page_text` returns nothing. These
steps are mandatory and are what the confidence score is based on.

1. **Cover it.** Zoom every `band(n)` from 0 to `bands-1`. Confirm each band's `scrollTop`
   advanced and the content differs from the previous one; the last must report `atEnd`.
   A repeated view means the scroller didn't move — do not summarise a truncated card.
2. **Bracket audit.** In Col. 10/11 a name or acquisition in `[ ]` is **struck off /
   superseded**; only unbracketed entries are live. Count total rows, bracketed, and live.
   On Byculla 1642, six of eight are bracketed and the live pair is entry 1 (MCGB, lessor)
   and entry 8 (Central View CHS, lessee). Getting this wrong inverts the answer.
3. **Re-read the ownership band once more** and diff against the first pass. Any
   disagreement on a name, date, deed no. or amount → mark that field `[unclear]`.
4. **Never guess.** An illegible digit is `[unclear]`, not a plausible value. Watermarks
   overlay the text and corrupt exactly these fields. Where the card itself is garbled or
   abbreviated (Byculla 1642 prints the lessor as `THE MUPL CORP OF GREATER B BAY`), quote
   it **as printed** and say how you are reading it — never silently normalise. That is a
   document quirk, not a legibility failure, so it doesn't lower the Legibility score.
5. **Compute, don't copy.** Lease expiry = start + term, stated explicitly.
6. **Sanity checks.** Last mutation date ≤ signing date; live lessee count ≥ 1 (0 is a
   red flag, not a conclusion); tenure code present.

**City** = English *Survey Register* (s.282 MLRC 1966), Cols 1–17. Tenure codes seen:
`MUNL` municipal lease, `CIT` City Improvement Trust, `LTA` leasehold-toka, `FH` freehold —
quote the code, don't invent a gloss. Col. 8B/9 may nest per-decade assessments and
`[REDEEMED]`.
**Suburban** = Marathi *मालमत्ता पत्रक* (Form 7, 1969 rules): PU-ID · गाव · तालुका/न.भू.का. ·
नगर भूमापन क्रमांक · शिट/प्लॉट · क्षेत्र चौ.मी. · धारणाधिकार (class, e.g. जी-1) ·
सुविधाधिकार · मूळ धारक · पट्टेदार · इतर भार, then the mutation table (दिनांक · व्यवहार ·
नविन धारक · फेरफार क्रमांक) — translate व्यवहार into plain English.

## 6. Output — lawyer-style summary, then a confidence block
Lead with the conclusion, then the evidence. Six blocks:

1. **The property** — address, area, sheet/register/page, signing date.
2. **Title as it stands today** — 3–4 lines: who holds the freehold, who holds under what
   instrument, since when, at what rent. **Unbracketed parties only.**
3. **Key dates** — table, oldest first: date · event · instrument no. · mutation no.
4. **How title flowed** — numbered chain, one line per transfer:
   `A → B, assignment 12-1-1948, deed 676, Rs 91,500 (superseded)`. Say who it ends with.
5. **Points to verify** — computed lease expiry, years of silence since the last mutation,
   MCGM / Trustees for the Improvement of the City of Bombay as lessor, statutory holders,
   blank Devolution of Title, area revised by later order, occupancy not evidenced.
6. **Confidence** — the table below.

Plain English throughout ("assignment", "surrender and regrant"), never column numbers.
Quote deed and mutation numbers so documents can be pulled. Close with the watermark
caveat — **For View Only, Not For Legal Purpose** — and
`digitalsatbara.mahabhumi.gov.in/dslr`. Set out what the record says and what remains to be
checked; do not give legal advice.

### Confidence rubric — score each, then take the **lowest** as overall
Never average: a title read is only as good as its weakest link.

| Dimension | High | Medium | Low |
|---|---|---|---|
| **Legibility** | every field read cleanly, both passes agree | 1–2 `[unclear]` in non-critical fields | any `[unclear]` in a party name, date, deed no., or area |
| **Completeness** | all bands covered, `atEnd` reached, all sections present | a section present but partly blank on the card | truncation suspected, or a band failed to advance |
| **Bracket clarity** | bracketing unambiguous, ≥1 live lessee identified | bracketing ambiguous on 1 entry | can't tell live from struck, or 0 live lessees |
| **Currency** | last mutation < 10 yrs | 10–30 yrs | > 30 yrs, or blank Devolution with a long chain |
| **Corroboration** | area agrees with the §8 independent source | — | independent area disagrees > 5% |

**Corroboration is scored only when an independent source exists** — i.e. Suburban plots,
via §8. For Mumbai City there is none, so mark it `n/a` and **exclude it from the minimum**
rather than letting it cap the score. A dimension that can never be satisfied is not a
measure of confidence, it's a constant.

State it as `Confidence: Medium — limited by Currency (last mutation 1972, 54 yrs)`. Always
name the binding dimension. **A Low on any scored dimension caps the overall at Low**, and
the summary must open with that caveat rather than burying it.

## 7. Batch mode (unattended)
Ask for these **once, up front**, then run without interrupting. The user can be AFK — the
captcha is read by vision, not by them.

**Required:** village (one for all, or paired per CTS) · the CTS list.
**Defaults, confirm only if changing:** mobile `9821114112` · sub-plot policy **fetch all
sub-plots** · not-found → record and continue · captcha → 3 retries then record and
continue · output = one combined table + a full summary per plot · JPEGs named
`propcard_<village>_<cts>.jpg`.

**Never block mid-batch.** Every ambiguity resolves by the stated policy and goes into an
**exceptions list** reported at the end: not-found, sub-plots taken, captcha failures, low
confidence, and any `[unclear]` field. Re-run `find` per plot (back resets everything).
Budget **30–60 s per plot** — 10 plots ≈ 5–10 min. Say the estimate before starting.

Deliverables: combined table (CTS · address · area · tenure · live lessee · lessor · last
mutation · confidence), then per-plot summaries, then exceptions. If the user wants the
JPEGs, get Downloads connected via `request_cowork_directory` **before** starting.

### Downloads: one file per batch, never N
**Chrome blocks repeated automatic downloads from an origin, and the block persists** —
once tripped, even a single later download fails silently, on a fresh page load. Verified:
after a 3-plot batch, two further download attempts produced no file at all.

So **never fire a download per plot in batch mode.** Stash each card and emit **one** file
at the end — a single download never trips the rule:

```javascript
// after submit(), instead of downloading:
stash=(cts,src)=>{const k='pc_'+cts; sessionStorage.setItem(k,src);
  const ix=JSON.parse(sessionStorage.getItem('pc_index')||'[]');
  if(!ix.includes(cts)){ix.push(cts);sessionStorage.setItem('pc_index',JSON.stringify(ix));}
  return ix.length};
// at the end of the batch — ONE download
emit=(village)=>{const ix=JSON.parse(sessionStorage.getItem('pc_index')||'[]');
  const html='<html><meta charset=utf-8><body style="margin:0">'+ix.map(c=>
    '<h3>CTS '+c+'</h3><img style="width:100%" src="'+sessionStorage.getItem('pc_'+c)+'">').join('')+'</body></html>';
  const u=URL.createObjectURL(new Blob([html],{type:'text/html'}));
  const a=document.createElement('a');a.href=u;a.download='propcards_'+village+'.html';
  document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);
  return ix.length};
```
`sessionStorage` survives same-tab navigation and holds ~5 MB ≈ **8 cards**; past that,
emit in chunks or switch to IndexedDB. Single lookups keep downloading one JPEG directly —
one file, so the rule never fires.

If the origin is **already** blocked, no code fixes it. Ask the user once: Chrome ⋮ →
Settings → Privacy and security → Site settings → Additional content settings → Automatic
downloads → Allow, adding `bhulekh.mahabhumi.gov.in`. Claude cannot do this — the extension
refuses `chrome://` pages and computer-use grants browsers read-only tier.

Either way, **verify the file landed** (`ls` the Downloads mount) and record a miss as an
exception, never a silent omission. Any post-processing of saved cards (stitching,
converting, OCR) runs through `uv run` — see Runtimes.

## 8. Optional pre-flight — BhuNaksha JSON (~120 ms, no captcha, Suburban)
MahaBhulekh has no API (every step `__doPostBack`, ~745 KB ViewState up / 1.3 MB down; the
cascade **cannot** be collapsed — injected option values are rejected and search silently
no-ops). The map service does:
`POST mahabhunakasha.mahabhumi.gov.in/rest/MapInfo/getPlotInfo` with `state, giscode,
plotno, srs` → `{area, info, gisinfo, the_geom}`; `info` gives CTS, plot area, **Dharna**,
sheet. Walk `/rest/VillageMapService/ListsAfterLevelGeoref` for `giscode`, or list a whole
village via `kidelistFromGisCodeMH`. Use it to confirm existence and read holding class —
**never report its area as the record area** (Marol 1590: it said 2011.70 vs the card's
2478.80; its polygon area 2471.25 was within 0.3%). No owners, no mutations. District codes
match MahaBhulekh, taluka codes do not. City coverage froze the tab — treat as Suburban only.

## Gotchas
- `$('btnBack')` **resets everything** — navigates to `NewBhulekh.aspx`, unchecks the
  Property Card radio, clears the cascade, and **issues a fresh captcha**. So there is
  **one captcha per plot; lookups cannot be batched behind one read.**
- Session expiry reverts the panel to 7/12. If controls revert, restart from §1.
- 7/12 = agricultural land outside the city survey; K-Prat = the older register. Neither
  answers a Mumbai plot query.
- Property Card ≠ DP reservation, zone or road width. Say so if asked — this skill covers
  title and tenure only.
- **Session anchor:** before the first lookup (and before any batch) run **Byculla 1640**
  → Register 179, Page 26, Sheet 284, **825.25 sq.m**, MUNL, Laughton's "Part of 3527".
  If that mismatches, the site changed — stop and report rather than trusting output.
- **Form Submit Button Selector:** Always click `#ContentPlaceHolder1_btnmainsubmit` after CAPTCHA input. Do not click `#ContentPlaceHolder1_btnsearch`.
- **Async Base64 Delivery:** Poll `#ContentPlaceHolder1_ImgPC` `src` attribute until `,` is present.
- **Fuzzy Village Lookup:** Normalize village names and token-match against dropdown options (e.g. `Malabar Hill` -> `Malabar-Cambala Hill`).
- **Structured Output Layout:** Organize plot assets inside 1 dedicated subfolder per query (`<village>_<cts>/`) containing `.jpg`, `.html`, `title_report_*.md`, `promoter_brief_*.md`, `lawyer_brief_*.md`, and `.json`. Generate `index.xlsx` (Master Excel Index with clickable hyperlinks to per-plot assets).
