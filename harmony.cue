package harmony

import (
  cuecsv "encoding/csv"
  "list"

  "universe.dagger.io/docker"
  "universe.dagger.io/git"
)

// Schema for project registration
Registration: {
  // git repository to clone
  remote: string

  // git ref to checkout
  ref: string

  // path to the registration
  path: string

  // testing cases
  cases: [string]: docker.#Run
  // often you will provide some short codes

  // versions injected into commands by the driver
  versions: [string]: string
  // do not fill, but can be referenced
  // particularly useful for short codes

  // feel free to add more fields for your needs
}

// Dagger actions for harmony
Harmony: {

  // version config 
  versions: [string]: string 

  // the registered projects
  registry: [string]: Registration

  // image tests are run in
  // ofter parameterized by the versions
  runner: docker.#Image

  // directory where users' code is cloned
  workdir: string

  // extra config
  extra: {
    // injected into the registrations
    reg: {...}
    // injected into the docker.#Run, per case
    run: {...}
  }

  // creates actions for each registration
  for name, reg in registry {
    (name): {
      _reg: reg & {
        extra.reg
        "versions": versions
      }
      // clone the remote
      clone: git.#Pull & {
        remote: _reg.remote
        ref: _reg.ref
        keepGitDir: true
      }

      // run a container for each case
      for key, case in _reg.cases {
        (key): docker.#Run & {
          always: true

          // setup base
          let R = runner
          input: R

          // embed case
          case

          // embed case run extra
          extra.run

          // where we put the source repository
          mounts: {
            work: {
              contents: clone.output
              dest: workdir 
            }
          }
        }
      }
    }
  }

  // used via 'cue eval -e actions.csv'
  // to get action list for use in scripts
  // see run.py for an example
  csv: cuecsv.Encode(list.FlattenN([
    for name, reg in registry {
      [ for key, case in reg.cases { [name, key] } ]
    }
  ], 1))
}
