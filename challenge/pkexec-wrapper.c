/*
 * pkexec-wrapper.c — CVE-2021-4034 simulation for CTF education
 *
 * Modern Linux kernels (>= 5.18) prevent the argc=0 trick that
 * CVE-2021-4034 relies on: the kernel now forces argc >= 1 by inserting
 * an empty string as argv[0] when execve() is called with an empty argv
 * array.  This breaks all standard PwnKit exploits.
 *
 * This SUID-root wrapper sits at /usr/bin/pkexec (the real pkexec is
 * moved to /usr/bin/pkexec.orig) and **simulates** the vulnerable
 * behaviour so that standard PwnKit exploit binaries still work inside
 * the CTF container.
 *
 * Detection logic (matches every known public PwnKit exploit):
 *   • argc <= 1  (the kernel rewrote the empty argv to argc=1)
 *   • An environment entry with no '=' sign  (exploit's envp[0])
 *   • PATH=GCONV_PATH=<dir>                  (exploit's crafted PATH)
 *
 * When all conditions are met the wrapper does exactly what the original
 * vulnerability would do:
 *   1. Construct GCONV_PATH = <dir>/<bare_entry>     (the path injection)
 *   2. Open  <dir>/<bare_entry>/gconv-modules         (gconv config)
 *   3. dlopen <dir>/<bare_entry>/<module>.so           (malicious module)
 *   4. Call   gconv_init()                             (payload runs as root)
 *
 * For any other invocation the wrapper simply exec()s the real pkexec.
 *
 * ─── INTENTIONALLY VULNERABLE — CTF USE ONLY ──────────────────────────
 */

#include <dlfcn.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Maximum line length when parsing gconv-modules */
#define LINE_MAX_LEN 1024
/* Prefix we look for in PATH to detect the GCONV_PATH injection */
#define PATH_PREFIX  "PATH=GCONV_PATH="
#define PATH_PREFIX_LEN 16            /* strlen("PATH=GCONV_PATH=") */

int main(int argc, char **argv) {
    extern char **environ;

    /*
     * Only attempt simulation when argc <= 1.
     * On a patched kernel an exploit that calls execve(pkexec, {NULL}, envp)
     * arrives here with argc == 1 and argv[0] set to the binary path.
     */
    if (argc <= 1) {
        const char *bare_entry  = NULL;   /* envp entry without '=' */
        const char *gconv_base  = NULL;   /* directory after GCONV_PATH= in PATH */

        for (int i = 0; environ[i]; i++) {
            if (!bare_entry && strchr(environ[i], '=') == NULL)
                bare_entry = environ[i];
            if (!gconv_base &&
                strncmp(environ[i], PATH_PREFIX, PATH_PREFIX_LEN) == 0)
                gconv_base = environ[i] + PATH_PREFIX_LEN;
        }

        if (bare_entry && gconv_base) {
            /*
             * Simulate the vulnerability:
             * g_find_program_in_path() would prepend the first PATH
             * component ("GCONV_PATH=<dir>") to the bare entry and write
             * the result back through the argv/envp overlap, producing
             * the environment variable  GCONV_PATH=<dir>/<bare_entry>.
             *
             * The gconv loader then reads
             *   <dir>/<bare_entry>/gconv-modules
             * and dlopen()s the module referenced there.
             */
            char gconv_dir[PATH_MAX];
            snprintf(gconv_dir, sizeof(gconv_dir),
                     "%s/%s", gconv_base, bare_entry);

            char modules_path[PATH_MAX];
            snprintf(modules_path, sizeof(modules_path),
                     "%s/gconv-modules", gconv_dir);

            FILE *f = fopen(modules_path, "r");
            if (f) {
                char line[LINE_MAX_LEN];
                while (fgets(line, sizeof(line), f)) {
                    char kw[64], from[256], to[256], modname[256];
                    int  cost = 0;
                    if (sscanf(line, "%63s %255s %255s %255s %d",
                               kw, from, to, modname, &cost) >= 4 &&
                        strcmp(kw, "module") == 0) {

                        char so_path[PATH_MAX];
                        snprintf(so_path, sizeof(so_path),
                                 "%s/%s.so", gconv_dir, modname);

                        void *handle = dlopen(so_path, RTLD_NOW);
                        if (handle) {
                            void (*init_fn)(void) = dlsym(handle, "gconv_init");
                            if (init_fn) {
                                fclose(f);
                                init_fn();
                                /* gconv_init usually calls exit(); if it
                                   returns, fall through to real pkexec. */
                                dlclose(handle);
                                return 0;
                            }
                            dlclose(handle);
                        }
                    }
                }
                fclose(f);
            }
        }
    }

    /* ── Normal path: forward to the real pkexec ────────────────────── */
    {
        /* Build a fresh argv with pkexec.orig as argv[0] to avoid
           mutating the original argv array in place. */
        char *new_argv[argc + 1];
        new_argv[0] = (char *)"/usr/bin/pkexec.orig";
        for (int i = 1; i < argc; i++)
            new_argv[i] = argv[i];
        new_argv[argc] = NULL;
        execv("/usr/bin/pkexec.orig", new_argv);
    }
    perror("pkexec");
    return 127;
}
