import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer, request as proxyRequest } from "node:http";
import { extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const FRONT_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)));
const PORT = Number(process.env.FRONT_PORT || 5173);
const API_HOST = process.env.API_HOST || "127.0.0.1";
const API_PORT = Number(process.env.API_PORT || 5000);
const CONTENT_TYPES = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
};

function isApiPath(pathname) {
  return (
    pathname.startsWith("/api/") ||
    pathname.startsWith("/auth/") ||
    pathname === "/perfil-anunciante" ||
    pathname.startsWith("/fotos-perfil/") ||
    pathname.startsWith("/media/") ||
    pathname === "/health" ||
    pathname === "/openapi"
  );
}

function proxyApi(request, response) {
  const upstream = proxyRequest(
    {
      hostname: API_HOST,
      port: API_PORT,
      path: request.url,
      method: request.method,
      headers: {
        ...request.headers,
        host: `${API_HOST}:${API_PORT}`,
      },
    },
    (upstreamResponse) => {
      response.writeHead(
        upstreamResponse.statusCode || 502,
        upstreamResponse.headers,
      );
      upstreamResponse.pipe(response);
    },
  );

  upstream.on("error", (error) => {
    console.error("API proxy request failed:", error.message);
    if (!response.headersSent) {
      response.writeHead(502, {
        "Content-Type": "application/json; charset=utf-8",
      });
      response.end(JSON.stringify({ message: "API indisponível." }));
    }
  });
  request.pipe(upstream);
}

async function serveFile(request, response, pathname) {
  if (!["GET", "HEAD"].includes(request.method)) {
    response.writeHead(405, { Allow: "GET, HEAD" });
    response.end();
    return;
  }

  let decodedPath;
  try {
    decodedPath = decodeURIComponent(pathname);
  } catch {
    response.writeHead(400);
    response.end();
    return;
  }

  let filePath = resolve(FRONT_ROOT, `.${decodedPath}`);
  if (filePath !== FRONT_ROOT && !filePath.startsWith(FRONT_ROOT + sep)) {
    response.writeHead(404);
    response.end();
    return;
  }

  try {
    if ((await stat(filePath)).isDirectory()) {
      filePath = resolve(filePath, "index.html");
    }
    const file = await stat(filePath);
    if (!file.isFile()) {
      response.writeHead(404);
      response.end();
      return;
    }
    response.writeHead(200, {
      "Content-Length": file.size,
      "Content-Type":
        CONTENT_TYPES[extname(filePath)] || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    if (request.method === "HEAD") {
      response.end();
      return;
    }
    createReadStream(filePath).pipe(response);
  } catch {
    response.writeHead(404);
    response.end();
  }
}

const server = createServer((request, response) => {
  const { pathname } = new URL(request.url, "http://localhost");
  if (isApiPath(pathname)) {
    proxyApi(request, response);
    return;
  }
  void serveFile(request, response, pathname);
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Frontend with API proxy listening on port ${PORT}`);
});
