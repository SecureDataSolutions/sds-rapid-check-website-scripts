# Pre-public security review

**Verdict — SHIP.** The saved-page check read the HTML and reported referenced script hosts with zero observed network calls. The review covered `3fa26dc40ed71370aa04ed61dab3da4ff53beb94`. No fix commit was needed.

| Check | Evidence |
| --- | --- |
| Files and history | Inspected the working files, workflow token references, Git blobs and commit metadata. Found no embedded credential, internal hostname or IP, workstation path, or workstation email. Commit identities use GitHub noreply addresses. |
| Offline mode | All four offline unit tests passed. An independent CLI check observed zero Python socket, URL-request or subprocess events with the saved fixture, a URL supplied as a filename, and saved HTML containing external base, script and frame references. The URL filename failed locally. |
| Online mode | The CLI fetches the supplied HTTP(S) page and reads up to 5 MiB plus one byte to detect truncation. Local redirect-handler checks accepted a same-host redirect and a standard HTTPS upgrade to a www alias. They rejected a different host, an HTTPS downgrade and a port change. Referenced scripts and frames are never fetched by the parser. |
| Checksums | `shasum -a 256 -c SHA256SUMS` passed for `third_party_scripts.py`. |
| README | Positional page addresses select online mode. Saved HTML requires `--file` and `--site` together. The latter supplies the page address for resolving references and identifying third-party hosts. The documented limits on dynamically added scripts and frames match the parser. |
| Reporting and license | `SECURITY.md` directs sensitive reports to GitHub private vulnerability reporting and contains no personal email. The MIT license is present. |

This review used local files and Git objects. The release download links and availability of the hosted reporting form were outside the local checks. Signed tags were intentionally omitted.
