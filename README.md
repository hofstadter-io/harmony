# dagger-unity

`harmony` is a framework for
testing a suite of repositories
across versions of dependencies.
Discover errors and regressions
in downstream projects before
releasing new code.
`harmony` makes it easy for both developers and users
to setup and register projects for usage in upstream testing.

Built on [Dagger](https://dagger.io), `harmony` provides

- single-file setup for developers
- simple registrations for users
- support for any languages or tools 
- consistent environment for testing
- simplified version injection

_Note, while `harmony` uses Dagger, this is not required downstream projects._


## Harmony Setup

To setup `harmony`, add the following file to your project.

```cue
```

## Registration Setup

There are two parts to registration

1. Add your project to the upstream `harmony` registry
2. Add your Registration definition to your own project

```cue
```


To add a new registration, add a file to `registry` like `self.cue`:

(and [open a pull request](https://github.com/hofstadter-io/dagger-unity/pulls))

Run registration cases or a single case with dagger: `dagger do <reg> [case]`.

Use `./run.py` to run the full suite of registrations and cases sequentially,
or as a convenient way to set dependency versions.

```cue
package registry

// Note the 'Registry: <name>: ...` needs to be unique
Registry: self: #Registration & {
  // 
  remote: "github.com/hofstadter-io/dagger-unity"
  ref: "main"

  cases: {
    // run any cue command
    cue:    { _cue: ["eval", "in.cue"], workdir: "/work/examples/cue" }
    // run a Go program, cue version assigned
    goapi:  { _goapi: "go run main.go", workdir: "/work/examples/go" }
    // run dagger, so pretty much anything
    dagger: { _dagger: "run", workdir: "/work/examples/dagger" }
    // run globs of testscript txtar files
    txtar:  { _testscript: "*.txt", workdir: "/work/examples/txtar" }
    // run arbitrary scripts in the testing container with available commands
    script: {
      workdir: "/work/examples/script"
      _script: """
      #!/usr/bin/env bash
      set -euo pipefail

      echo "a bash script"
      pwd
      ls
      ./run.sh
      """
    }
  }
}
```

You can create your own private registries and include private repositories
by using the `#Unity` from the testers. This is how this repository works.

```cue
// from dagger.cue
// ...

dagger.#Plan

client: network: "unix:///var/run/docker.sock": connect: dagger.#Socket

actions: {
  // versions which will be injected 
  versions: {
    cue:    string | *"v0.4.3-beta.2"
    dagger: string | *"v0.2.4"
    go:     string | *"1.18"
  }

  // the image tests should run in
  runner: base.Image & {
    "versions": versions
  }

  // dagger actions injected from registry
  testers.#Unity & {
    // required fields
    "runner": runner
    "registry": registry.Registry
    // extra information to inject
    extra: reg: "versions": versions
    extra: run: {
      mounts: {
        // for dagger-in-dagger
        docker: {
          contents: client.network."unix:///var/run/docker.sock".connect
          dest:     "/var/run/docker.sock"
        }
      }
    }
  }
}
```

---

`harmony` was inspired by the idea
of merging Dagger and [cue-unity](https://github.com/cue-unity/unity),
where the goal is to collect community projects
and run them against new CUE language changes.

Todo:

- rename to `harmony`
- move more to users' repos
  - reg is repo/ref/path
  - cases in target repo
  - make it easy to use / test locally in target repo
- make reuse easier
  - move #Unity up a dir
  - unity plan so users can test locally
  - import #Registration
  - make shorts not hidden
- add more CUE projects
- create hof "Harmony"

