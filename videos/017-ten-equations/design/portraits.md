# Portrait candidates for video 017 (chapter cards)

**Status (2026-11-26): batch 1 downloaded, minus Navier.** Chapter 4 is a names-only card. The 8 originals are in
`assets/images/portraits/src/`, each SHA-1 checked against Commons. The cards are built by `scripts/portraits.py`
into `assets/images/portraits/<key>.png` (contact sheet: `design/portraits.png`). Credits are in
`assets/images/portraits/CREDITS.md`. The list below is kept as the record of what was considered.

All files are on Wikimedia Commons. I checked each file's licence, author, date and size through the Commons API on
2026-11-26; nothing has been downloaded yet. The chapter card shows the portrait 2.2 u tall, which is about 300 px at
1080p and about 600 px at 4K, so a file needs to be roughly 600 px tall or more. Every portrait is duotoned in its
chapter hue and feathered into black (`components.png`). Storage: `assets/images/portraits/<name>.<ext>`, with the
credits in `assets/images/portraits/CREDITS.md`.

## Batch 1 (recommended): 9 files, about 12 MB in total

| ch | subject | Commons file | author, date | licence | size |
|---|---|---|---|---|---|
| 1 | James Clerk Maxwell | [James-Clerk-Maxwell-1831-1879.jpg](https://commons.wikimedia.org/wiki/File:James-Clerk-Maxwell-1831-1879.jpg) | unknown photographer, c. 1870 | Public domain | 819 × 1024, 109 KB |
| 2 | Albert Einstein (1915 chapter) | [Einstein_1921_by_F_Schmutzer_-_restoration.jpg](https://commons.wikimedia.org/wiki/File:Einstein_1921_by_F_Schmutzer_-_restoration.jpg) | Ferdinand Schmutzer, 1921 (restoration: Adam Cuerden) | Public domain | 2523 × 3313, 2.6 MB |
| 3 | Erwin Schrödinger | [Erwin_Schrödinger_-_Narodowe_Archiwum_Cyfrowe_(1-E-939).jpg](https://commons.wikimedia.org/wiki/File:Erwin_Schr%C3%B6dinger_-_Narodowe_Archiwum_Cyfrowe_(1-E-939).jpg) | unknown, 1933 (Polish National Digital Archive) | Public domain | 2534 × 3500, 1.5 MB |
| 4 | Claude-Louis Navier | [Claude-Louis_Navier.jpg](https://commons.wikimedia.org/wiki/File:Claude-Louis_Navier.jpg) | unknown engraving | Public domain | **231 × 303, 65 KB (too small; see note)** |
| 4 | George Gabriel Stokes | [Portrait_of_George_Gabriel_Stokes_…(2551115803).jpg](https://commons.wikimedia.org/wiki/File:Portrait_of_George_Gabriel_Stokes_(1819-1903),_Physicist_and_Mathematician_(2551115803).jpg) | Smithsonian Institution Libraries | No known copyright restrictions | 918 × 1464, 339 KB |
| 5 | Joseph Fourier | [Fourier2_-_restoration1.jpg](https://commons.wikimedia.org/wiki/File:Fourier2_-_restoration1.jpg) | Julien-Léopold Boilly, engraving, early 19th c. | Public domain | 1619 × 2048, 2.6 MB |
| 6 | Albert Einstein (1905 chapter) | [Einstein_patentoffice.jpg](https://commons.wikimedia.org/wiki/File:Einstein_patentoffice.jpg) | Lucien Chavan, 1904 or 1905 (Einstein Archives, Jerusalem) | Public domain | 4360 × 5699, 3.4 MB |
| 7 | Augustin-Louis Cauchy | [Cauchy_Augustin_Louis_dibner_coll_SIL14-C2-03a.jpg](https://commons.wikimedia.org/wiki/File:Cauchy_Augustin_Louis_dibner_coll_SIL14-C2-03a.jpg) | Louis Grégoire & Deneux, lithograph, c. 1840 (Smithsonian Dibner coll.) | Public domain | 1000 × 1508, 300 KB |
| 8 | Claude Shannon | [C.E._Shannon._Tekniska_museet_43069_(2x3_crop).jpg](https://commons.wikimedia.org/wiki/File:C.E._Shannon._Tekniska_museet_43069_(2x3_crop).jpg) | Bell Telephone Laboratories, c. 1956 (Tekniska museet) | Public domain (published without a copyright notice) | 1465 × 2196, 635 KB |

Chapter 6 shows the young Einstein of 1905, so it doesn't repeat the chapter 2 portrait.

## Alternates (not in the batch)
| subject | file | why not first choice |
|---|---|---|
| Maxwell | [James_Clerk_Maxwell_gravure.jpg](https://commons.wikimedia.org/wiki/File:James_Clerk_Maxwell_gravure.jpg), CC0, 1339 × 2000 | an engraving, sharper but less recognisable than the photograph |
| Einstein | [Albert_Einstein_Head_cleaned.jpg](https://commons.wikimedia.org/wiki/File:Albert_Einstein_Head_cleaned.jpg), Orren Jack Turner 1947, PD, 8.7 MB | the famous late portrait, 32 years after the 1915 equations |
| Cauchy | [French_School_-_Portrait_of_Augustin-Louis_Cauchy_(1789-1857).jpg](https://commons.wikimedia.org/wiki/File:French_School_-_Portrait_of_Augustin-Louis_Cauchy_(1789-1857).jpg), PD, 626 × 711 | Wikipedia's lead image, but smaller |

## Names only (no portrait on the card)
| subject | reason |
|---|---|
| Thomas Bayes | The only portrait in circulation (a 1936 reprint) is very likely not Bayes |
| Fischer Black | The Commons file is a 2009 user upload of a modern photo marked "public domain"; that licence isn't reliable |
| Myron Scholes | CC BY-SA 3.0 only (Lindau 2008); needs attribution and share-alike, so it isn't public domain |
| Robert C. Merton | CC BY-SA 4.0 only (MIT 2010); same reason |

## Notes
- **Navier is too small** (303 px tall, about half of what 4K needs), and Commons has no larger portrait of him. There
  are three options:
  - (a) Use it anyway. The duotone and the feather hide most of the softness, and it would sit at 50 % size beside Stokes.
  - (b) Give chapter 4 a names-only card, "Navier 1822 · Stokes 1845".
  - (c) Show Stokes only.

  I recommend (b): chapter 4 credits two people, and showing one face beside a blurred one looks uneven.
- **What "public domain" covers.** The Commons tags mean public domain in the United States, where YouTube hosts the
  video. Three files rest on how the photo was published rather than on the photographer's age:
  - Shannon: published by Bell Labs in 1956 without a copyright notice.
  - Schrödinger (1933): Polish archive.
  - The Einstein 1904/05 photo by Lucien Chavan, who died in 1942.

  These are the usual tags for these well-known images. If you want zero ambiguity, the safest set is the engravings
  and lithographs (Fourier, Cauchy, Navier) plus the Maxwell, Stokes and Schmutzer files.
- Credits will go in the video description: subject, author, source and licence, one line each.
