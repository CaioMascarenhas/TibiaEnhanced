import { test } from "node:test";
import assert from "node:assert/strict";
import { parseReleases, getPackage, formatSize } from "../src/lib/releases.ts";

const root = "https://github.com/CaioMascarenhas/TibiaEnhanced/releases";
const file = (name, overrides = {}) => ({
  name,
  size: 1048576,
  browser_download_url: `${root}/download/v1/${name}`,
  ...overrides,
});
const release = (overrides = {}) => ({
  id: 1,
  tag_name: "v1",
  name: "Version 1",
  html_url: `${root}/tag/v1`,
  draft: false,
  prerelease: true,
  published_at: "2026-10-01T12:00:00Z",
  assets: [
    file("TibiaEnhanced-v1-windows-x64-setup.exe"),
    file("TibiaEnhanced-v1-windows-x64-portable.zip"),
  ],
  ...overrides,
});

test("includes prereleases and sorts by publication rather than array order", () => {
  const parsed = parseReleases([
    release(),
    release({ id: 2, published_at: "2026-10-20T12:00:00Z", prerelease: false }),
  ]);
  assert.deepEqual(
    parsed.map((r) => r.id),
    [2, 1],
  );
  assert.equal(parsed[1].prerelease, true);
});
test("ignores drafts, source archives, malformed releases and empty releases", () => {
  assert.deepEqual(
    parseReleases([
      release({ draft: true }),
      release({ assets: [file("Source code.zip")] }),
      release({ published_at: "invalid" }),
      null,
      {},
    ]),
    [],
  );
  assert.throws(() => parseReleases({ message: "rate limit exceeded" }));
});
test("does not offer untrusted download destinations", () => {
  assert.deepEqual(
    parseReleases([
      release({
        assets: [
          file("TibiaEnhanced-windows-x64-setup.exe", {
            browser_download_url: "https://example.com/file.exe",
          }),
        ],
      }),
    ]),
    [],
  );
  assert.deepEqual(
    parseReleases([
      release({ html_url: "https://github.com/another/repo/releases/tag/v1" }),
    ]),
    [],
  );
});
test("handles a release with just one available package", () => {
  const [parsed] = parseReleases([
    release({ assets: [file("TibiaEnhanced-v1-windows-x64-portable.zip")] }),
  ]);
  assert.equal(getPackage(parsed, "installer"), undefined);
  assert.equal(getPackage(parsed, "portable").size, 1048576);
  assert.equal(formatSize(1048576), "1 MB");
});
