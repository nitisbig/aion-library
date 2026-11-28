# Pronunciation guide, video 015

Words the voice might get wrong. **Alias** means `voice.toml [aliases]` swaps the spelling sent to ElevenLabs; the
captions keep the script's spelling, and possessives follow ("Euler's" becomes "Oiler's"). Every alias and every
"listen" entry gets checked by ear in the speed test (checkpoint 1); fix by editing `[aliases]`, which only
re-requests the scenes that use the word.

## Spoken names

| Word | Say it | Alias | Scenes | Note |
|---|---|---|---|---|
| Euler, Euler's | OY-ler | `Oiler` | ch3_s05, ch4_s04, ch5_s03, ch7_s02, out_s02 | TTS often says "YOO-ler". |
| Buffon | boo-FAWN (French *Buffon*, nasal end) | `Boo-fon` | ch6_s05 | Listen: should not sound like "buffoon". |
| Zu Chongzhi, Chongzhi's | dzoo chong-JUR (Mandarin *Zǔ Chōngzhī*) | `Chong-jur` for Chongzhi | ch2_s02, ch6_s05 | "Zu" left as "zoo", a common English reading. |
| Lazzarini | lat-sa-REE-nee | none | ch6_s05 | Listen: Italian *zz* is "ts". |
| Leibniz | LIBE-nits | none | ch5_s02 | Listen: not "LEEB-nits". |
| Bernoulli | ber-NOO-lee | none | ch6_s02 | |
| Archimedes | ar-kih-MEE-deez | none | ch2_s02, ch5_s06 | |
| Pythagoras | pih-THAG-or-us | none | ch1_s03, ch2_s04 | |
| Cantor (Georg) | KAN-tor (GAY-org) | none | ch1_s03 | |
| Lambert (Johann) | LAM-bert (YO-hahn) | none | ch2_s05 | |
| Hamilton (William Rowan) | ROH-un | none | ch3_s07 | |
| Wiles (Andrew) | WILES | none | ch7_s04 | |
| Harry Beck | | none | ch4_s06 | |
| Monte Carlo | MON-tee KAR-loh | none | ch6_s06 | |

## Math words

| Word | Say it | Alias | Scenes | Note |
|---|---|---|---|---|
| pi | PIE | none | many | |
| e (the constant) | EE | none | ch3_s05, ch5_s03, ch7_s02 | Listen: a lone "e" can be swallowed. If so, write "the number e" in the narration. |
| i (the quarter turn) | EYE | none | ch3_s04, ch3_s05, ch3_s06, ch7_s02 | Written `*i*` in the script. |
| quaternions | kwuh-TUR-nee-unz | none | ch3_s07 | |
| cyclic (group) | SY-klik | none | ch3_s03 | Both SY-klik and SIK-lik are fine; listen for consistency. |
| topology, topologist | tuh-POL-uh-jee, tuh-POL-uh-jist | none | ch4 | |
| irrational, rational | | none | ch2 | |
| x ("Solve for x") | EKS | none | in_s01 | |

## Written on screen, never spoken
Reuleaux triangle (ruh-LOH), Lindemann, isomorphism, aleph-null, theta, chi (Euler characteristic, KYE). If any
of these move into the narration, add a row here first.

## Numbers and the URL
Every number in the narration is already spelled the way it is said ("nineteen-oh-one", "three hundred fifty-five
over one hundred thirteen", "two point seven one eight"), and `scripts/lint_script.py` rejects digits.
The site is read as "I give ideas dot com"; the end card shows `igiveideas.com`.
