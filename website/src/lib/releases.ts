export type ReleaseAsset = {
  name: string;
  browser_download_url: string;
  size: number;
};
export type Release = {
  id: number;
  tag_name: string;
  name: string;
  html_url: string;
  published_at: string;
  prerelease: boolean;
  assets: ReleaseAsset[];
};

const owner = "caiomascarenhas";
const repository = "tibiaenhanced";

function isRepositoryUrl(value: unknown, download = false): value is string {
  if (typeof value !== "string") return false;
  try {
    const url = new URL(value);
    const prefix = `/${owner}/${repository}/releases/`;
    return (
      url.protocol === "https:" &&
      url.hostname === "github.com" &&
      url.pathname
        .toLowerCase()
        .startsWith(prefix + (download ? "download/" : "tag/"))
    );
  } catch {
    return false;
  }
}

export function getPackage(release: Release, format: "installer" | "portable") {
  return release.assets.find((a) =>
    format === "installer"
      ? /windows.*x64.*setup\.exe$/i.test(a.name)
      : /windows.*x64.*portable\.zip$/i.test(a.name),
  );
}

/** Public releases only. Do not guess download filenames or expose draft/source archives. */
export function parseReleases(data: unknown): Release[] {
  if (!Array.isArray(data)) throw new Error("Resposta de releases inválida.");
  const result: Release[] = [];
  for (const row of data) {
    if (
      !row ||
      typeof row !== "object" ||
      row.draft !== false ||
      typeof row.id !== "number" ||
      typeof row.tag_name !== "string" ||
      !isRepositoryUrl(row.html_url) ||
      !Number.isFinite(Date.parse(row.published_at)) ||
      !Array.isArray(row.assets)
    )
      continue;
    const assets: ReleaseAsset[] = row.assets.filter(
      (a: Partial<ReleaseAsset>) =>
        a &&
        typeof a.name === "string" &&
        isRepositoryUrl(a.browser_download_url, true) &&
        typeof a.size === "number" &&
        a.size > 0,
    );
    const release: Release = {
      id: row.id,
      tag_name: row.tag_name,
      name: typeof row.name === "string" && row.name ? row.name : row.tag_name,
      html_url: row.html_url,
      published_at: row.published_at,
      prerelease: row.prerelease === true,
      assets,
    };
    if (getPackage(release, "installer") || getPackage(release, "portable"))
      result.push(release);
  }
  return result.sort(
    (a, b) => Date.parse(b.published_at) - Date.parse(a.published_at),
  );
}

export const formatSize = (bytes: number) =>
  `${(bytes / 1024 / 1024).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} MB`;
