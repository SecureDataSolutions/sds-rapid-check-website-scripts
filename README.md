# SDS Rapid Check: Website Third-Party Scripts

Lists third-party script hosts referenced in a page's HTML. On November 16, 2026, attackers added malicious JavaScript to some Optimizely Web Experimentation customer projects.

## About

**Secure Data Solutions (SDS)**, https://sdsitgroup.com  
The engineers other security teams call when it has to work.

We build free tools like this for cyber defenders. Our programs cover threat exposure, defensible security, and validated resilience: we find what attackers can reach, shut it down, and prove it holds.

Ran this and found something, or not sure what you're looking at? Drop us a line at https://sdsitgroup.com. We're happy to talk it through, and when it's urgent, we pick up.

Read the script first. [third_party_scripts.py](third_party_scripts.py)

Requires Python 3.8 or later.

## macOS

```sh
base='https://github.com/SecureDataSolutions/sds-rapid-check-website-scripts/releases/latest/download'
curl -fsSLo third_party_scripts.py "$base/third_party_scripts.py" &&
curl -fsSLo SHA256SUMS "$base/SHA256SUMS" &&
shasum -a 256 -c SHA256SUMS &&
python3 -I -B -S third_party_scripts.py https://www.example.com
```

Use a site you own or are authorized to check.

### Offline

In your browser, save the page as **Webpage, HTML Only**. Then set `--site` to the page's original address. The saved HTML is read locally and no network request is made.

```sh
python3 -I -B -S third_party_scripts.py --file ./page.html --site https://www.example.com
```

## Linux

```sh
base='https://github.com/SecureDataSolutions/sds-rapid-check-website-scripts/releases/latest/download'
curl -fsSLo third_party_scripts.py "$base/third_party_scripts.py" &&
curl -fsSLo SHA256SUMS "$base/SHA256SUMS" &&
sha256sum -c SHA256SUMS &&
python3 -I -B -S third_party_scripts.py https://www.example.com
```

Use a site you own or are authorized to check.

### Offline

In your browser, save the page as **Webpage, HTML Only**. Then set `--site` to the page's original address. The saved HTML is read locally and no network request is made.

```sh
python3 -I -B -S third_party_scripts.py --file ./page.html --site https://www.example.com
```

## Windows (PowerShell)

```powershell
& {
$ErrorActionPreference = 'Stop'
$base = 'https://github.com/SecureDataSolutions/sds-rapid-check-website-scripts/releases/latest/download'
Invoke-WebRequest "$base/third_party_scripts.py" -OutFile .\third_party_scripts.py
Invoke-WebRequest "$base/SHA256SUMS" -OutFile .\SHA256SUMS
$entries = @(Get-Content .\SHA256SUMS | Where-Object { $_ -match '^([0-9a-fA-F]{64})  third_party_scripts\.py$' })
if ($entries.Count -ne 1) { throw 'Expected one SHA-256 entry for third_party_scripts.py' }
$expected = $entries[0].Substring(0, 64).ToLowerInvariant()
$actual = (Get-FileHash .\third_party_scripts.py -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'third_party_scripts.py SHA-256 verification failed' }
py -3 -I -B -S .\third_party_scripts.py https://www.example.com
}
```

Use a site you own or are authorized to check.

### Offline

In Edge, Chrome, or another browser, open the page you are authorized to check. Save it as **Webpage, HTML Only**. Set `--site` to the page's original address.

```powershell
py -3 -I -B -S .\third_party_scripts.py --file .\page.html --site https://www.example.com
```

## What a result means

The check lists script hosts present in the saved or fetched HTML. It does not inspect scripts added later by JavaScript, scripts inside frames, or other pages. It does not determine whether a listed script is safe.

No finding is not proof of no compromise.

## Sources

- [Optimizely Web Experimentation security incident report](https://pages.optimizely.com/rs/947-RKE-048/images/Security%20Incident%20Report%20-%20Optimizely%20Web%20Experimentation%20-%20Nov%2017%202026.pdf)

## Want the full check?

The AI Coding Tool Check covers up to five developer machines and one build pipeline. The fixed price is $1,250 for the first three teams.

[Contact form](https://sdsitgroup.com/contact) · [Services](https://sdsitgroup.com/#services)

Run only on systems you own or are authorized to check. Licensed under the MIT License.
