'''
## pdk_projen

This package contains a set of [Projen](https://github.com/projen/projen) project types which can be used to
configure complex project configuration through code.

These project types synthesize project configuration files such as package.json, .gitignore, nx.json, eslint, jest, etc
from well-typed definitions.

## Prerequisites

Ensure you have the following packages installed globally:

* [node > 14](https://nodejs.org/en/download/package-manager/) (or use [nvm](https://github.com/nvm-sh/nvm#installing-and-updating) to install)

## Getting Started

To create a new project, run the following command and follow the instructions for the specific project type below:

```shell
mkdir my-project
cd my-project
npx projen new --from aws-prototyping-sdk <project-type>
```

The following are the currently supported project types, along with instructions on how to get started:

* [nx-monorepo](#nx-monorepo) - Vends a [NX](https://github.com/nrwl/nx) based monorepo with support for
  polygot builds.

## nx-monorepo

The `nx-monorepo` project type will bootstrap a [NX](https://github.com/nrwl/nx) based monorepo with support for
polygot builds, build caching, dependency graph visualization and much more.

This project type does the heavy lifting of managing your packages/subprojects to be compatible with NX by performing
the following actions:

* Generates an `nx.json` file in the root directory which is responsible for configuring project defaults including
  what targets should be cached, what implicit dependencies there are, etc.
* Generate a `package.json` for any non-node project. This is needed as a facade so that nx can call a target, regardless
  of language. All targets in this package.json file defer to projen tasks.
* Installs a plugin (owned by pdk) which handles polygot dependency linking.

After running the `npx projen new --from aws-prototyping-sdk nx-monorepo` command, a `.projenrc.ts` will be created which
looks like this:

```python
import { pdk_projen } from "aws-prototyping-sdk";

const project = new pdk_projen.NxMonorepoProject({
  defaultReleaseBranch: "main",
  devDeps: ["aws-prototyping-sdk"],
  name: "my-project",
});

project.synth();
```

This will be the main mechanism for adding new subprojects, configuring/changing aspects of the generated
packages, etc.

### Adding Subprojects

Now that you have a monorepo set up, it's time to add Subprojects. You can add Subprojects by simply
instantiating new instances of classes which extend the native Projen's
[Project](https://github.com/projen/projen/blob/main/src/project.ts) class, and providing the monorepo project as a
[parent](https://projen.io/api/API.html#projen-project).

Examples of currently supported project types are listed on the
[Projen Github Website](https://github.com/projen/projen#getting-started).

#### Example 1 - Explicit dependencies

NX ships pre-configured to detect explicit dependencies within the package.json files of Sub projects. If your
use case relies solely on Typescript then this example will apply to you.

Let's create a sample application with two Subprojects:

1. An Infrastructure project based on Typescript which creates some basic CDK infrastructure.
2. A React webapp written in Typescript.

```python
import { pdk_projen } from "aws-prototyping-sdk";
import { AwsCdkTypeScriptApp } from "projen/lib/awscdk";
import { ReactTypeScriptProject } from "projen/lib/web";

const project = new pdk_projen.NxMonorepoProject({
  defaultReleaseBranch: "main",
  devDeps: ["aws-prototyping-sdk"],
  name: "my-project",
});

const webapp = new ReactTypeScriptProject({
  defaultReleaseBranch: "mainline",
  name: "webapp",
  parent: project,
  outdir: "packages/webapp",
});

new AwsCdkTypeScriptApp({
  cdkVersion: "2.0.0",
  defaultReleaseBranch: "mainline",
  name: "infra",
  devDeps: [webapp.package.packageName], // CDK App depends on the webapp
  parent: project,
  outdir: "packages/infra",
});

project.synth();
```

**It is important to note that both the `parent` and `outdir` properties are mandatory.**

Now from the root directory, we will synthesize these packages by running `npx projen`. After
running this command we will notice our directory will resemble the following:

```
root
  |- packages
        |- infra
        |- webapp
```

The `npx projen` command would have also linked these two packages by adding a dev dependency to webapp in infra's
package.json and also updating the `workspace` property in the root package.json.

If we wanted to build infra, we can run the following command: `npx nx build infra`.

```shell
 npx nx build infra

 >  NX   Running target build for project infra and 1 task(s) it depends on

 —————————————————————————————————————————————————————————————————————————————————
 > nx build webapp
 ...
 Done in 12.06s.

 > nx build infra
 ...
 Done in 25.59s.

 —————————————————————————————————————————————————————————————————————————————————

 >  NX   Successfully ran target build for project infra

```

As you can see from the above logs, the webapp build target was executed first as this is a dependency
of infra. NX will also cache builds, so if the same command is re-run (without modifying anything) you will notice the
build completes in a fraction of the time.

#### Example 2 - Implicit dependencies

Some project require implementing components in different languages and as such a mechanism must exist
to declare implicit build dependencies between these various packages.

Let's extend the previous example by adding an additional python based lambda as follows:

```python
import { pdk_projen } from "aws-prototyping-sdk";
import { AwsCdkTypeScriptApp } from "projen/lib/awscdk";
import { ReactTypeScriptProject } from "projen/lib/web";
import { PythonProject } from "projen/lib/python";

const project = new pdk_projen.NxMonorepoProject({
  defaultReleaseBranch: "main",
  devDeps: ["aws-prototyping-sdk"],
  name: "my-project",
});

const webapp = new ReactTypeScriptProject({
  defaultReleaseBranch: "mainline",
  name: "webapp",
  parent: project,
  outdir: "packages/webapp",
});

const infra = new AwsCdkTypeScriptApp({
  cdkVersion: "2.0.0",
  defaultReleaseBranch: "mainline",
  name: "infra",
  devDeps: [webapp.package.packageName], // CDK App depends on the webapp
  parent: project,
  outdir: "packages/infra",
});

const lambda = new PythonProject({
  authorEmail: "foo@bar.com",
  authorName: "foo bar",
  moduleName: "python_lambda",
  name: "python_lambda",
  version: "0.0.0",
  parent: project,
  outdir: "packages/python_lambda",
});

project.addImplicitDependency(infra, lambda);

project.synth();
```

Now from the root directory, we will synthesize these packages by running `npx projen`. After
running this command we will notice our directory will resemble the following:

```
root
  |- packages
        |- infra
        |- webapp
        |- lambda
```

If we wanted to build infra, we can run the following command: `npx nx run infra:build`.

```shell
 npx nx build infra

 >  NX   Running target build for project infra and 2 task(s) it depends on
 ———————————————————————————————————————————————————————————————————————————————

 > nx build python_lambda
 ...
 Done in 0.62s.

 > nx build webapp
 ...
 Done in 10.79s.

 > nx build infra
 ...
 Done in 22.65s.

 —————————————————————————————————————————————————————————————————————————————————

 >  NX   Successfully ran target build for project infra
```

As you can see from the above logs, the build was executed sequentially for each package in the correct
order.

### FAQ

#### How do I run a target just on a specific package?

To run a package specific target, you can do the following:

```shell
cd packages/<my-package>
npx projen <target>
```

#### How do I add a new target to a projen Sub Project?

In your `.projenrc.ts`, do the following:

```python
const infra = new AwsCdkTypeScriptApp({
  cdkVersion: "2.0.0",
  defaultReleaseBranch: "mainline",
  name: "infra",
  devDeps: [webapp.package.packageName], // CDK App depends on the webapp
  parent: project,
  outdir: "packages/infra",
});

infra.addTask("new-target", {
  exec: "echo \"hi\""
});
```

As usual, ensure you run `npx projen` in the root directory to synthesize your change.

From here is it just a case of executing `npx projen new-target` in the package directory.

#### I have added a project in .projenrc.ts but it isn't synthesizing?

1. Ensure that the `parent` property of the project is set to the monorepo project.
2. Ensure that an `outdir` is configured i.e: `packages/mypackage`.
3. run `npx projen` in the root of the monorepo.

#### How do I visualize my dependencies?

From the root of the monorepo run `npx nx graph`. This will open a browser showing how all your packages are related.

#### I have updated a dependency, however the build or graph viz is not detecting any changes.

1. Ensure you have run `npx projen` from the root of the monorepo.
2. Sometimes the nx cache can become stale and can be cleared by running `npx nx clear-cache`.

#### How do I build everything in my monorepo without a specific target package?

`npx nx run-many --target=build --all`

#### I am running a different target, however the dependencies are not being executed.

By default, only the `build` target is configured to rely on it's dependencies. To configure additional targets, update
the NXMonorepoProject as follows:

```python
const project = new pdk_projen.NxMonorepoProject({
  defaultReleaseBranch: "main",
  devDeps: ["aws-prototyping-sdk"],
  name: "my-project",
  targetDependencies: {
    test: [
      {
        target: "test",
        projects: "dependencies",
      }
    ]
  }
});
```

In this example, the test target will now wait until the test target has run successfully in all dependent projects.

#### My subproject is not caching even though I haven't changed anything.

This can happen if NX detects changes in generated/compiled files. Examples of this include if your build
target creates a zip file or generates test artifacts with timestamps. To resolve this, add an nxIgnore pattern as follows:

```python
const project = new pdk_projen.NxMonorepoProject({
  defaultReleaseBranch: "main",
  devDeps: ["aws-prototyping-sdk"],
  name: "my-project",
  nxIgnorePatterns: ["generated-tst", "dist"]
});
```

As per the above configuration, NX will ignore anything within `generated-tst` or `dist` folders within any
package in your monorepo.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import projen
import projen.awscdk
import projen.github
import projen.github.workflows
import projen.javascript
import projen.python
import projen.release
import projen.typescript


class NxMonorepoProject(
    projen.typescript.TypeScriptProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-prototyping-sdk.pdk_projen.NxMonorepoProject",
):
    '''This project type will bootstrap a NX based monorepo with support for polygot builds, build caching, dependency graph visualization and much more.

    :pjid: nx-monorepo
    '''

    def __init__(
        self,
        *,
        nx_ignore_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample_language: typing.Optional["SampleLanguage"] = None,
        target_dependencies: typing.Optional[typing.Mapping[builtins.str, typing.Sequence["TargetDependency"]]] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.javascript.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_projen_upgrades: typing.Optional[builtins.bool] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[projen.github.workflows.Triggers] = None,
        bundler_options: typing.Optional[projen.javascript.BundlerOptions] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[projen.javascript.UpgradeDependenciesOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.javascript.JestOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[projen.javascript.PrettierOptions] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_upgrade_auto_merge: typing.Optional[builtins.bool] = None,
        projen_upgrade_schedule: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_upgrade_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_git_identity: typing.Optional[projen.github.GitIdentity] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[projen.javascript.CodeArtifactOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.javascript.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.javascript.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.javascript.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[projen.release.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
    ) -> None:
        '''
        :param nx_ignore_patterns: List of patterns to include in the .nxignore file. Default: []
        :param sample_language: Language to generate sample code on first synthesis. Default: undefined
        :param target_dependencies: Configuration for NX TargetDependencies. Default: {}
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_projen_upgrades: (experimental) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for depsUpgrade. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_upgrade_auto_merge: (deprecated) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param projen_upgrade_schedule: (experimental) Customize the projenUpgrade schedule in cron expression. Default: [ "0 6 * * *" ]
        :param projen_upgrade_secret: (deprecated) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``). This setting is a GitHub secret name which contains a GitHub Access Token with ``repo`` and ``workflow`` permissions. This token is used to submit the upgrade pull request, which will likely include workflow updates. To create a personal access token see https://github.com/settings/tokens Default: - no automatic projen upgrade pull requests
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        '''
        options = NxMonorepoProjectOptions(
            nx_ignore_patterns=nx_ignore_patterns,
            sample_language=sample_language,
            target_dependencies=target_dependencies,
            disable_tsconfig=disable_tsconfig,
            docgen=docgen,
            docs_directory=docs_directory,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            libdir=libdir,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            sample_code=sample_code,
            srcdir=srcdir,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            typescript_version=typescript_version,
            default_release_branch=default_release_branch,
            artifacts_directory=artifacts_directory,
            auto_approve_projen_upgrades=auto_approve_projen_upgrades,
            auto_approve_upgrades=auto_approve_upgrades,
            build_workflow=build_workflow,
            build_workflow_triggers=build_workflow_triggers,
            bundler_options=bundler_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            gitignore=gitignore,
            jest=jest,
            jest_options=jest_options,
            mutable_build=mutable_build,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            package=package,
            prettier=prettier,
            prettier_options=prettier_options,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_js_options=projenrc_js_options,
            projen_upgrade_auto_merge=projen_upgrade_auto_merge,
            projen_upgrade_schedule=projen_upgrade_schedule,
            projen_upgrade_secret=projen_upgrade_secret,
            projen_version=projen_version,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            release=release,
            release_to_npm=release_to_npm,
            release_workflow=release_workflow,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            auto_approve_options=auto_approve_options,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            allow_library_dependencies=allow_library_dependencies,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_detect_bin=auto_detect_bin,
            bin=bin,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            bundled_deps=bundled_deps,
            code_artifact_options=code_artifact_options,
            deps=deps,
            description=description,
            dev_deps=dev_deps,
            entrypoint=entrypoint,
            homepage=homepage,
            keywords=keywords,
            license=license,
            licensed=licensed,
            max_node_version=max_node_version,
            min_node_version=min_node_version,
            npm_access=npm_access,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            package_manager=package_manager,
            package_name=package_name,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            repository=repository,
            repository_directory=repository_directory,
            scripts=scripts,
            stability=stability,
            jsii_release_version=jsii_release_version,
            major_version=major_version,
            npm_dist_tag=npm_dist_tag,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_trigger=release_trigger,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            versionrc_options=versionrc_options,
            workflow_container_image=workflow_container_image,
            workflow_runs_on=workflow_runs_on,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addImplicitDependency")
    def add_implicit_dependency(
        self,
        dependent: projen.Project,
        dependee: projen.Project,
    ) -> None:
        '''Create an implicit dependency between two Project's.

        This is typically
        used in polygot repos where a Typescript project wants a build dependency
        on a Python project as an example.

        :param dependent: project you want to have the dependency.
        :param dependee: project you wish to depend on.
        '''
        return typing.cast(None, jsii.invoke(self, "addImplicitDependency", [dependent, dependee]))

    @jsii.member(jsii_name="preSynthesize")
    def pre_synthesize(self) -> None:
        '''Called before all components are synthesized.

        :inheritDoc: true
        '''
        return typing.cast(None, jsii.invoke(self, "preSynthesize", []))

    @jsii.member(jsii_name="synth")
    def synth(self) -> None:
        '''Synthesize all project files into ``outdir``.

        1. Call "this.preSynthesize()"
        2. Delete all generated files
        3. Synthesize all sub-projects
        4. Synthesize all components of this project
        5. Call "postSynthesize()" for all components of this project
        6. Call "this.postSynthesize()"

        :inheritDoc: true
        '''
        return typing.cast(None, jsii.invoke(self, "synth", []))


@jsii.data_type(
    jsii_type="aws-prototyping-sdk.pdk_projen.NxMonorepoProjectOptions",
    jsii_struct_bases=[projen.typescript.TypeScriptProjectOptions],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "allow_library_dependencies": "allowLibraryDependencies",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_detect_bin": "autoDetectBin",
        "bin": "bin",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "bundled_deps": "bundledDeps",
        "code_artifact_options": "codeArtifactOptions",
        "deps": "deps",
        "description": "description",
        "dev_deps": "devDeps",
        "entrypoint": "entrypoint",
        "homepage": "homepage",
        "keywords": "keywords",
        "license": "license",
        "licensed": "licensed",
        "max_node_version": "maxNodeVersion",
        "min_node_version": "minNodeVersion",
        "npm_access": "npmAccess",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "scripts": "scripts",
        "stability": "stability",
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "npm_dist_tag": "npmDistTag",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_trigger": "releaseTrigger",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "versionrc_options": "versionrcOptions",
        "workflow_container_image": "workflowContainerImage",
        "workflow_runs_on": "workflowRunsOn",
        "default_release_branch": "defaultReleaseBranch",
        "artifacts_directory": "artifactsDirectory",
        "auto_approve_projen_upgrades": "autoApproveProjenUpgrades",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "build_workflow": "buildWorkflow",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bundler_options": "bundlerOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "gitignore": "gitignore",
        "jest": "jest",
        "jest_options": "jestOptions",
        "mutable_build": "mutableBuild",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "package": "package",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_js_options": "projenrcJsOptions",
        "projen_upgrade_auto_merge": "projenUpgradeAutoMerge",
        "projen_upgrade_schedule": "projenUpgradeSchedule",
        "projen_upgrade_secret": "projenUpgradeSecret",
        "projen_version": "projenVersion",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "release": "release",
        "release_to_npm": "releaseToNpm",
        "release_workflow": "releaseWorkflow",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "disable_tsconfig": "disableTsconfig",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "libdir": "libdir",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "sample_code": "sampleCode",
        "srcdir": "srcdir",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "typescript_version": "typescriptVersion",
        "nx_ignore_patterns": "nxIgnorePatterns",
        "sample_language": "sampleLanguage",
        "target_dependencies": "targetDependencies",
    },
)
class NxMonorepoProjectOptions(projen.typescript.TypeScriptProjectOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[projen.javascript.CodeArtifactOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.javascript.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.javascript.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.javascript.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[projen.release.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_projen_upgrades: typing.Optional[builtins.bool] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[projen.github.workflows.Triggers] = None,
        bundler_options: typing.Optional[projen.javascript.BundlerOptions] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[projen.javascript.UpgradeDependenciesOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.javascript.JestOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[projen.javascript.PrettierOptions] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_upgrade_auto_merge: typing.Optional[builtins.bool] = None,
        projen_upgrade_schedule: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_upgrade_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_git_identity: typing.Optional[projen.github.GitIdentity] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.javascript.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        nx_ignore_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample_language: typing.Optional["SampleLanguage"] = None,
        target_dependencies: typing.Optional[typing.Mapping[builtins.str, typing.Sequence["TargetDependency"]]] = None,
    ) -> None:
        '''Configuration options for the NxMonorepoProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_projen_upgrades: (experimental) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for depsUpgrade. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_upgrade_auto_merge: (deprecated) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param projen_upgrade_schedule: (experimental) Customize the projenUpgrade schedule in cron expression. Default: [ "0 6 * * *" ]
        :param projen_upgrade_secret: (deprecated) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``). This setting is a GitHub secret name which contains a GitHub Access Token with ``repo`` and ``workflow`` permissions. This token is used to submit the upgrade pull request, which will likely include workflow updates. To create a personal access token see https://github.com/settings/tokens Default: - no automatic projen upgrade pull requests
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param nx_ignore_patterns: List of patterns to include in the .nxignore file. Default: []
        :param sample_language: Language to generate sample code on first synthesis. Default: undefined
        :param target_dependencies: Configuration for NX TargetDependencies. Default: {}
        '''
        if isinstance(logging, dict):
            logging = projen.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = projen.ProjenrcOptions(**projenrc_json_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = projen.github.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = projen.github.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = projen.github.GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = projen.github.MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = projen.SampleReadmeProps(**readme)
        if isinstance(stale_options, dict):
            stale_options = projen.github.StaleOptions(**stale_options)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = projen.javascript.CodeArtifactOptions(**code_artifact_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = projen.javascript.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = projen.github.workflows.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = projen.javascript.BundlerOptions(**bundler_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = projen.github.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = projen.javascript.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(jest_options, dict):
            jest_options = projen.javascript.JestOptions(**jest_options)
        if isinstance(prettier_options, dict):
            prettier_options = projen.javascript.PrettierOptions(**prettier_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = projen.javascript.ProjenrcOptions(**projenrc_js_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = projen.github.GitIdentity(**workflow_git_identity)
        if isinstance(eslint_options, dict):
            eslint_options = projen.javascript.EslintOptions(**eslint_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = projen.typescript.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(tsconfig, dict):
            tsconfig = projen.javascript.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = projen.javascript.TypescriptConfigOptions(**tsconfig_dev)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "default_release_branch": default_release_branch,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if bin is not None:
            self._values["bin"] = bin
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if deps is not None:
            self._values["deps"] = deps
        if description is not None:
            self._values["description"] = description
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if scripts is not None:
            self._values["scripts"] = scripts
        if stability is not None:
            self._values["stability"] = stability
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if auto_approve_projen_upgrades is not None:
            self._values["auto_approve_projen_upgrades"] = auto_approve_projen_upgrades
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if package is not None:
            self._values["package"] = package
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projen_upgrade_auto_merge is not None:
            self._values["projen_upgrade_auto_merge"] = projen_upgrade_auto_merge
        if projen_upgrade_schedule is not None:
            self._values["projen_upgrade_schedule"] = projen_upgrade_schedule
        if projen_upgrade_secret is not None:
            self._values["projen_upgrade_secret"] = projen_upgrade_secret
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if release is not None:
            self._values["release"] = release
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if libdir is not None:
            self._values["libdir"] = libdir
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if nx_ignore_patterns is not None:
            self._values["nx_ignore_patterns"] = nx_ignore_patterns
        if sample_language is not None:
            self._values["sample_language"] = sample_language
        if target_dependencies is not None:
            self._values["target_dependencies"] = target_dependencies

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[projen.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[projen.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[projen.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[projen.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[projen.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[projen.ProjenrcOptions], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[projen.github.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[projen.github.AutoApproveOptions], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[projen.github.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[projen.github.AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[projen.github.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[projen.github.GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[projen.github.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[projen.github.MergifyOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[projen.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[projen.ProjectType], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[projen.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[projen.SampleReadmeProps], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[projen.github.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[projen.github.StaleOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Author's Organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[projen.javascript.CodeArtifactOptions]:
        '''(experimental) Options for publishing npm package to AWS CodeArtifact.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[projen.javascript.CodeArtifactOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'express', 'lodash', 'foo@^2' ]
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'typescript', '@types/express' ]
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``).

        Set to an empty string to not include ``main`` in your package.json

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum node.js version to require via ``engines`` (inclusive).

        :default: - no max

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive).

        :default: - no "engines" specified

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[projen.javascript.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[projen.javascript.NpmAccess], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[projen.javascript.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[projen.javascript.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[projen.javascript.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[projen.javascript.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_trigger(self) -> typing.Optional[projen.release.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[projen.release.ReleaseTrigger], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with standard-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_release_branch(self) -> builtins.str:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        assert result is not None, "Required property 'default_release_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_projen_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_approve_projen_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[projen.github.workflows.Triggers]:
        '''(experimental) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[projen.github.workflows.Triggers], result)

    @builtins.property
    def bundler_options(self) -> typing.Optional[projen.javascript.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[projen.javascript.BundlerOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(self) -> typing.Optional[projen.github.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[projen.github.DependabotOptions], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[projen.javascript.UpgradeDependenciesOptions]:
        '''(experimental) Options for depsUpgrade.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[projen.javascript.UpgradeDependenciesOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[projen.javascript.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[projen.javascript.JestOptions], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(self) -> typing.Optional[projen.javascript.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[projen.javascript.PrettierOptions], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js_options(self) -> typing.Optional[projen.javascript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[projen.javascript.ProjenrcOptions], result)

    @builtins.property
    def projen_upgrade_auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: false

        :deprecated: use ``autoApproveProjenUpgrades``.

        :stability: deprecated
        '''
        result = self._values.get("projen_upgrade_auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projen_upgrade_schedule(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Customize the projenUpgrade schedule in cron expression.

        :default: [ "0 6 * * *" ]

        :stability: experimental
        '''
        result = self._values.get("projen_upgrade_schedule")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def projen_upgrade_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``).

        This setting is a GitHub secret name which contains a GitHub Access Token
        with ``repo`` and ``workflow`` permissions.

        This token is used to submit the upgrade pull request, which will likely
        include workflow updates.

        To create a personal access token see https://github.com/settings/tokens

        :default: - no automatic projen upgrade pull requests

        :deprecated: use ``githubTokenSecret`` instead.

        :stability: deprecated
        '''
        result = self._values.get("projen_upgrade_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_bootstrap_steps(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def workflow_git_identity(self) -> typing.Optional[projen.github.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[projen.github.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version to use in GitHub workflows.

        :default: - same as ``minNodeVersion``

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(self) -> typing.Optional[projen.javascript.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[projen.javascript.EslintOptions], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(self) -> typing.Optional[projen.typescript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[projen.typescript.ProjenrcOptions], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``.

        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(self) -> typing.Optional[projen.javascript.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[projen.javascript.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[projen.javascript.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[projen.javascript.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nx_ignore_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of patterns to include in the .nxignore file.

        :default: []

        :link: https://nx.dev/configuration/packagejson#nxignore
        '''
        result = self._values.get("nx_ignore_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sample_language(self) -> typing.Optional["SampleLanguage"]:
        '''Language to generate sample code on first synthesis.

        :default: undefined
        '''
        result = self._values.get("sample_language")
        return typing.cast(typing.Optional["SampleLanguage"], result)

    @builtins.property
    def target_dependencies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List["TargetDependency"]]]:
        '''Configuration for NX TargetDependencies.

        :default: {}

        :link: https://nx.dev/configuration/packagejson#target-dependencies
        '''
        result = self._values.get("target_dependencies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List["TargetDependency"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NxMonorepoProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-prototyping-sdk.pdk_projen.PDKPipelinePyProjectOptions",
    jsii_struct_bases=[projen.awscdk.AwsCdkPythonAppOptions],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "version": "version",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "license": "license",
        "poetry_options": "poetryOptions",
        "setup_config": "setupConfig",
        "module_name": "moduleName",
        "deps": "deps",
        "dev_deps": "devDeps",
        "pip": "pip",
        "poetry": "poetry",
        "projenrc_python": "projenrcPython",
        "projenrc_python_options": "projenrcPythonOptions",
        "pytest": "pytest",
        "pytest_options": "pytestOptions",
        "sample": "sample",
        "setuptools": "setuptools",
        "venv": "venv",
        "venv_options": "venvOptions",
        "build_command": "buildCommand",
        "cdkout": "cdkout",
        "context": "context",
        "feature_flags": "featureFlags",
        "require_approval": "requireApproval",
        "watch_excludes": "watchExcludes",
        "watch_includes": "watchIncludes",
        "cdk_version": "cdkVersion",
        "cdk_assert": "cdkAssert",
        "cdk_assertions": "cdkAssertions",
        "cdk_dependencies": "cdkDependencies",
        "cdk_dependencies_as_deps": "cdkDependenciesAsDeps",
        "cdk_test_dependencies": "cdkTestDependencies",
        "cdk_version_pinning": "cdkVersionPinning",
        "constructs_version": "constructsVersion",
        "app_entrypoint": "appEntrypoint",
        "testdir": "testdir",
    },
)
class PDKPipelinePyProjectOptions(projen.awscdk.AwsCdkPythonAppOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        module_name: builtins.str,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[projen.python.ProjenrcOptions] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[projen.python.PytestOptions] = None,
        sample: typing.Optional[builtins.bool] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional[projen.python.VenvOptions] = None,
        build_command: typing.Optional[builtins.str] = None,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[projen.awscdk.ApprovalLevel] = None,
        watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version: builtins.str,
        cdk_assert: typing.Optional[builtins.bool] = None,
        cdk_assertions: typing.Optional[builtins.bool] = None,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
        cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version_pinning: typing.Optional[builtins.bool] = None,
        constructs_version: typing.Optional[builtins.str] = None,
        app_entrypoint: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration options for the PDKPipelinePyProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: true
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. Default: false
        :param projenrc_python: (experimental) Use projenrc in python. This will install ``projen`` as a python dependency and will add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true if the project type is library
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: true
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param build_command: (experimental) A command to execute before synthesis. This command will be called when running ``cdk synth`` or when ``cdk watch`` identifies a change in your source code before redeployment. Default: - no build command
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param watch_excludes: (experimental) Glob patterns to exclude from ``cdk watch``. Default: []
        :param watch_includes: (experimental) Glob patterns to include in ``cdk watch``. Default: []
        :param cdk_version: (experimental) Minimum version of the AWS CDK to depend on. Default: "2.1.0"
        :param cdk_assert: (deprecated) Warning: NodeJS only. Install the @aws-cdk/assert library? Default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0
        :param cdk_assertions: (experimental) Install the assertions library? Only needed for CDK 1.x. If using CDK 2.x then assertions is already included in 'aws-cdk-lib' Default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0
        :param cdk_dependencies: (deprecated) Which AWS CDKv1 modules this project requires.
        :param cdk_dependencies_as_deps: (deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``). This is to ensure that downstream consumers actually have your CDK dependencies installed when using npm < 7 or yarn, where peer dependencies are not automatically installed. If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure they are present during development. Note: this setting only applies to construct library projects Default: true
        :param cdk_test_dependencies: (deprecated) AWS CDK modules required for testing.
        :param cdk_version_pinning: (experimental) Use pinned version instead of caret version for CDK. You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates. If you use experimental features this will let you define the moment you include breaking changes.
        :param constructs_version: (experimental) Minimum version of the ``constructs`` library to depend on. Default: - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is "10.0.5".
        :param app_entrypoint: (experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default). Default: "app.py"
        :param testdir: (experimental) Python sources directory. Default: "tests"
        '''
        if isinstance(logging, dict):
            logging = projen.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = projen.ProjenrcOptions(**projenrc_json_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = projen.github.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = projen.github.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = projen.github.GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = projen.github.MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = projen.SampleReadmeProps(**readme)
        if isinstance(stale_options, dict):
            stale_options = projen.github.StaleOptions(**stale_options)
        if isinstance(poetry_options, dict):
            poetry_options = projen.python.PoetryPyprojectOptionsWithoutDeps(**poetry_options)
        if isinstance(projenrc_python_options, dict):
            projenrc_python_options = projen.python.ProjenrcOptions(**projenrc_python_options)
        if isinstance(pytest_options, dict):
            pytest_options = projen.python.PytestOptions(**pytest_options)
        if isinstance(venv_options, dict):
            venv_options = projen.python.VenvOptions(**venv_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "author_email": author_email,
            "author_name": author_name,
            "version": version,
            "module_name": module_name,
            "cdk_version": cdk_version,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if license is not None:
            self._values["license"] = license
        if poetry_options is not None:
            self._values["poetry_options"] = poetry_options
        if setup_config is not None:
            self._values["setup_config"] = setup_config
        if deps is not None:
            self._values["deps"] = deps
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if pip is not None:
            self._values["pip"] = pip
        if poetry is not None:
            self._values["poetry"] = poetry
        if projenrc_python is not None:
            self._values["projenrc_python"] = projenrc_python
        if projenrc_python_options is not None:
            self._values["projenrc_python_options"] = projenrc_python_options
        if pytest is not None:
            self._values["pytest"] = pytest
        if pytest_options is not None:
            self._values["pytest_options"] = pytest_options
        if sample is not None:
            self._values["sample"] = sample
        if setuptools is not None:
            self._values["setuptools"] = setuptools
        if venv is not None:
            self._values["venv"] = venv
        if venv_options is not None:
            self._values["venv_options"] = venv_options
        if build_command is not None:
            self._values["build_command"] = build_command
        if cdkout is not None:
            self._values["cdkout"] = cdkout
        if context is not None:
            self._values["context"] = context
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if require_approval is not None:
            self._values["require_approval"] = require_approval
        if watch_excludes is not None:
            self._values["watch_excludes"] = watch_excludes
        if watch_includes is not None:
            self._values["watch_includes"] = watch_includes
        if cdk_assert is not None:
            self._values["cdk_assert"] = cdk_assert
        if cdk_assertions is not None:
            self._values["cdk_assertions"] = cdk_assertions
        if cdk_dependencies is not None:
            self._values["cdk_dependencies"] = cdk_dependencies
        if cdk_dependencies_as_deps is not None:
            self._values["cdk_dependencies_as_deps"] = cdk_dependencies_as_deps
        if cdk_test_dependencies is not None:
            self._values["cdk_test_dependencies"] = cdk_test_dependencies
        if cdk_version_pinning is not None:
            self._values["cdk_version_pinning"] = cdk_version_pinning
        if constructs_version is not None:
            self._values["constructs_version"] = constructs_version
        if app_entrypoint is not None:
            self._values["app_entrypoint"] = app_entrypoint
        if testdir is not None:
            self._values["testdir"] = testdir

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[projen.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[projen.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[projen.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[projen.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[projen.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[projen.ProjenrcOptions], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[projen.github.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[projen.github.AutoApproveOptions], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[projen.github.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[projen.github.AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[projen.github.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[projen.github.GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[projen.github.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[projen.github.MergifyOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[projen.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[projen.ProjectType], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[projen.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[projen.SampleReadmeProps], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[projen.github.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[projen.github.StaleOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> builtins.str:
        '''(experimental) Author's e-mail.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_email")
        assert result is not None, "Required property 'author_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_name(self) -> builtins.str:
        '''(experimental) Author's name.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author_name")
        assert result is not None, "Required property 'author_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the package.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package.

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def poetry_options(
        self,
    ) -> typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps]:
        '''(experimental) Additional options to set for poetry if using poetry.

        :stability: experimental
        '''
        result = self._values.get("poetry_options")
        return typing.cast(typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps], result)

    @builtins.property
    def setup_config(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        result = self._values.get("setup_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def module_name(self) -> builtins.str:
        '''(experimental) Name of the python package as used in imports and filenames.

        Must only consist of alphanumeric characters and underscores.

        :default: $PYTHON_MODULE_NAME

        :stability: experimental
        '''
        result = self._values.get("module_name")
        assert result is not None, "Required property 'module_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project.

        Dependencies use the format: ``<module>@<semver>``

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dev dependencies for this project.

        Dependencies use the format: ``<module>@<semver>``

        Additional dependencies can be added via ``project.addDevDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pip with a requirements.txt file to track project dependencies.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def poetry(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing.

        :default: false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("poetry")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_python(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in python.

        This will install ``projen`` as a python dependency and will add a ``synth``
        task which will run ``.projenrc.py``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_python")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_python_options(self) -> typing.Optional[projen.python.ProjenrcOptions]:
        '''(experimental) Options related to projenrc in python.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_python_options")
        return typing.cast(typing.Optional[projen.python.ProjenrcOptions], result)

    @builtins.property
    def pytest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include pytest tests.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pytest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pytest_options(self) -> typing.Optional[projen.python.PytestOptions]:
        '''(experimental) pytest options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("pytest_options")
        return typing.cast(typing.Optional[projen.python.PytestOptions], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sample code and test if the relevant directories don't exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def setuptools(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use setuptools with a setup.py script for packaging and publishing.

        :default: - true if the project type is library

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("setuptools")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use venv to manage a virtual environment for installing dependencies inside.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("venv")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv_options(self) -> typing.Optional[projen.python.VenvOptions]:
        '''(experimental) Venv options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("venv_options")
        return typing.cast(typing.Optional[projen.python.VenvOptions], result)

    @builtins.property
    def build_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) A command to execute before synthesis.

        This command will be called when
        running ``cdk synth`` or when ``cdk watch`` identifies a change in your source
        code before redeployment.

        :default: - no build command

        :stability: experimental
        '''
        result = self._values.get("build_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdkout(self) -> typing.Optional[builtins.str]:
        '''(experimental) cdk.out directory.

        :default: "cdk.out"

        :stability: experimental
        '''
        result = self._values.get("cdkout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional context to include in ``cdk.json``.

        :default: - no additional context

        :stability: experimental
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include all feature flags in cdk.json.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[projen.awscdk.ApprovalLevel]:
        '''(experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them.

        :default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[projen.awscdk.ApprovalLevel], result)

    @builtins.property
    def watch_excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to exclude from ``cdk watch``.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("watch_excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def watch_includes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to include in ``cdk watch``.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("watch_includes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_version(self) -> builtins.str:
        '''(experimental) Minimum version of the AWS CDK to depend on.

        :default: "2.1.0"

        :stability: experimental
        '''
        result = self._values.get("cdk_version")
        assert result is not None, "Required property 'cdk_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdk_assert(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Warning: NodeJS only.

        Install the @aws-cdk/assert library?

        :default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0

        :deprecated: The

        :stability: deprecated
        :aws-cdk: /assertions (in V1) and included in ``aws-cdk-lib`` for V2.
        '''
        result = self._values.get("cdk_assert")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_assertions(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the assertions library?

        Only needed for CDK 1.x. If using CDK 2.x then
        assertions is already included in 'aws-cdk-lib'

        :default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0

        :stability: experimental
        '''
        result = self._values.get("cdk_assertions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Which AWS CDKv1 modules this project requires.

        :deprecated: For CDK 2.x use "deps" instead. (or "peerDeps" if you're building a library)

        :stability: deprecated
        '''
        result = self._values.get("cdk_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_dependencies_as_deps(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``).

        This is to ensure that downstream consumers actually have your CDK dependencies installed
        when using npm < 7 or yarn, where peer dependencies are not automatically installed.
        If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure
        they are present during development.

        Note: this setting only applies to construct library projects

        :default: true

        :deprecated: Not supported in CDK v2.

        :stability: deprecated
        '''
        result = self._values.get("cdk_dependencies_as_deps")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_test_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) AWS CDK modules required for testing.

        :deprecated: For CDK 2.x use 'devDeps' (in node.js projects) or 'testDeps' (in java projects) instead

        :stability: deprecated
        '''
        result = self._values.get("cdk_test_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_version_pinning(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pinned version instead of caret version for CDK.

        You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates.
        If you use experimental features this will let you define the moment you include breaking changes.

        :stability: experimental
        '''
        result = self._values.get("cdk_version_pinning")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def constructs_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum version of the ``constructs`` library to depend on.

        :default:

        - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is
        "10.0.5".

        :stability: experimental
        '''
        result = self._values.get("constructs_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default).

        :default: "app.py"

        :stability: experimental
        '''
        result = self._values.get("app_entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Python sources directory.

        :default: "tests"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PDKPipelinePyProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PDKPipelineTsProject(
    projen.awscdk.AwsCdkTypeScriptApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-prototyping-sdk.pdk_projen.PDKPipelineTsProject",
):
    '''Synthesizes a Typescript Project with a CI/CD pipeline.

    :pjid: pdk-pipeline-ts
    '''

    def __init__(
        self,
        *,
        app_entrypoint: typing.Optional[builtins.str] = None,
        integration_test_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_options: typing.Optional[projen.awscdk.LambdaFunctionCommonOptions] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.javascript.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        build_command: typing.Optional[builtins.str] = None,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[projen.awscdk.ApprovalLevel] = None,
        watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version: builtins.str,
        cdk_assert: typing.Optional[builtins.bool] = None,
        cdk_assertions: typing.Optional[builtins.bool] = None,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
        cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version_pinning: typing.Optional[builtins.bool] = None,
        constructs_version: typing.Optional[builtins.str] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_projen_upgrades: typing.Optional[builtins.bool] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[projen.github.workflows.Triggers] = None,
        bundler_options: typing.Optional[projen.javascript.BundlerOptions] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[projen.javascript.UpgradeDependenciesOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.javascript.JestOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[projen.javascript.PrettierOptions] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_upgrade_auto_merge: typing.Optional[builtins.bool] = None,
        projen_upgrade_schedule: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_upgrade_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_git_identity: typing.Optional[projen.github.GitIdentity] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[projen.javascript.CodeArtifactOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.javascript.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.javascript.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.javascript.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[projen.release.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
    ) -> None:
        '''
        :param app_entrypoint: (experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default). Default: "main.ts"
        :param integration_test_auto_discover: (experimental) Automatically discovers and creates integration tests for each ``.integ.ts`` file in under your test directory. Default: true
        :param lambda_auto_discover: (experimental) Automatically adds an ``awscdk.LambdaFunction`` for each ``.lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param lambda_options: (experimental) Common options for all AWS Lambda functions. Default: - default options
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param build_command: (experimental) A command to execute before synthesis. This command will be called when running ``cdk synth`` or when ``cdk watch`` identifies a change in your source code before redeployment. Default: - no build command
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param watch_excludes: (experimental) Glob patterns to exclude from ``cdk watch``. Default: []
        :param watch_includes: (experimental) Glob patterns to include in ``cdk watch``. Default: []
        :param cdk_version: (experimental) Minimum version of the AWS CDK to depend on. Default: "2.1.0"
        :param cdk_assert: (deprecated) Warning: NodeJS only. Install the @aws-cdk/assert library? Default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0
        :param cdk_assertions: (experimental) Install the assertions library? Only needed for CDK 1.x. If using CDK 2.x then assertions is already included in 'aws-cdk-lib' Default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0
        :param cdk_dependencies: (deprecated) Which AWS CDKv1 modules this project requires.
        :param cdk_dependencies_as_deps: (deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``). This is to ensure that downstream consumers actually have your CDK dependencies installed when using npm < 7 or yarn, where peer dependencies are not automatically installed. If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure they are present during development. Note: this setting only applies to construct library projects Default: true
        :param cdk_test_dependencies: (deprecated) AWS CDK modules required for testing.
        :param cdk_version_pinning: (experimental) Use pinned version instead of caret version for CDK. You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates. If you use experimental features this will let you define the moment you include breaking changes.
        :param constructs_version: (experimental) Minimum version of the ``constructs`` library to depend on. Default: - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is "10.0.5".
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_projen_upgrades: (experimental) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for depsUpgrade. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_upgrade_auto_merge: (deprecated) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param projen_upgrade_schedule: (experimental) Customize the projenUpgrade schedule in cron expression. Default: [ "0 6 * * *" ]
        :param projen_upgrade_secret: (deprecated) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``). This setting is a GitHub secret name which contains a GitHub Access Token with ``repo`` and ``workflow`` permissions. This token is used to submit the upgrade pull request, which will likely include workflow updates. To create a personal access token see https://github.com/settings/tokens Default: - no automatic projen upgrade pull requests
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        '''
        options = PDKPipelineTsProjectOptions(
            app_entrypoint=app_entrypoint,
            integration_test_auto_discover=integration_test_auto_discover,
            lambda_auto_discover=lambda_auto_discover,
            lambda_options=lambda_options,
            disable_tsconfig=disable_tsconfig,
            docgen=docgen,
            docs_directory=docs_directory,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            libdir=libdir,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            sample_code=sample_code,
            srcdir=srcdir,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            typescript_version=typescript_version,
            build_command=build_command,
            cdkout=cdkout,
            context=context,
            feature_flags=feature_flags,
            require_approval=require_approval,
            watch_excludes=watch_excludes,
            watch_includes=watch_includes,
            cdk_version=cdk_version,
            cdk_assert=cdk_assert,
            cdk_assertions=cdk_assertions,
            cdk_dependencies=cdk_dependencies,
            cdk_dependencies_as_deps=cdk_dependencies_as_deps,
            cdk_test_dependencies=cdk_test_dependencies,
            cdk_version_pinning=cdk_version_pinning,
            constructs_version=constructs_version,
            default_release_branch=default_release_branch,
            artifacts_directory=artifacts_directory,
            auto_approve_projen_upgrades=auto_approve_projen_upgrades,
            auto_approve_upgrades=auto_approve_upgrades,
            build_workflow=build_workflow,
            build_workflow_triggers=build_workflow_triggers,
            bundler_options=bundler_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            gitignore=gitignore,
            jest=jest,
            jest_options=jest_options,
            mutable_build=mutable_build,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            package=package,
            prettier=prettier,
            prettier_options=prettier_options,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_js_options=projenrc_js_options,
            projen_upgrade_auto_merge=projen_upgrade_auto_merge,
            projen_upgrade_schedule=projen_upgrade_schedule,
            projen_upgrade_secret=projen_upgrade_secret,
            projen_version=projen_version,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            release=release,
            release_to_npm=release_to_npm,
            release_workflow=release_workflow,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            auto_approve_options=auto_approve_options,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            allow_library_dependencies=allow_library_dependencies,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_detect_bin=auto_detect_bin,
            bin=bin,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            bundled_deps=bundled_deps,
            code_artifact_options=code_artifact_options,
            deps=deps,
            description=description,
            dev_deps=dev_deps,
            entrypoint=entrypoint,
            homepage=homepage,
            keywords=keywords,
            license=license,
            licensed=licensed,
            max_node_version=max_node_version,
            min_node_version=min_node_version,
            npm_access=npm_access,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            package_manager=package_manager,
            package_name=package_name,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            repository=repository,
            repository_directory=repository_directory,
            scripts=scripts,
            stability=stability,
            jsii_release_version=jsii_release_version,
            major_version=major_version,
            npm_dist_tag=npm_dist_tag,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_trigger=release_trigger,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            versionrc_options=versionrc_options,
            workflow_container_image=workflow_container_image,
            workflow_runs_on=workflow_runs_on,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
        )

        jsii.create(self.__class__, self, [options])


@jsii.data_type(
    jsii_type="aws-prototyping-sdk.pdk_projen.PDKPipelineTsProjectOptions",
    jsii_struct_bases=[projen.awscdk.AwsCdkTypeScriptAppOptions],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "allow_library_dependencies": "allowLibraryDependencies",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_detect_bin": "autoDetectBin",
        "bin": "bin",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "bundled_deps": "bundledDeps",
        "code_artifact_options": "codeArtifactOptions",
        "deps": "deps",
        "description": "description",
        "dev_deps": "devDeps",
        "entrypoint": "entrypoint",
        "homepage": "homepage",
        "keywords": "keywords",
        "license": "license",
        "licensed": "licensed",
        "max_node_version": "maxNodeVersion",
        "min_node_version": "minNodeVersion",
        "npm_access": "npmAccess",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "scripts": "scripts",
        "stability": "stability",
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "npm_dist_tag": "npmDistTag",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_trigger": "releaseTrigger",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "versionrc_options": "versionrcOptions",
        "workflow_container_image": "workflowContainerImage",
        "workflow_runs_on": "workflowRunsOn",
        "default_release_branch": "defaultReleaseBranch",
        "artifacts_directory": "artifactsDirectory",
        "auto_approve_projen_upgrades": "autoApproveProjenUpgrades",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "build_workflow": "buildWorkflow",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bundler_options": "bundlerOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "gitignore": "gitignore",
        "jest": "jest",
        "jest_options": "jestOptions",
        "mutable_build": "mutableBuild",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "package": "package",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_js_options": "projenrcJsOptions",
        "projen_upgrade_auto_merge": "projenUpgradeAutoMerge",
        "projen_upgrade_schedule": "projenUpgradeSchedule",
        "projen_upgrade_secret": "projenUpgradeSecret",
        "projen_version": "projenVersion",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "release": "release",
        "release_to_npm": "releaseToNpm",
        "release_workflow": "releaseWorkflow",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "disable_tsconfig": "disableTsconfig",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "libdir": "libdir",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "sample_code": "sampleCode",
        "srcdir": "srcdir",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "typescript_version": "typescriptVersion",
        "build_command": "buildCommand",
        "cdkout": "cdkout",
        "context": "context",
        "feature_flags": "featureFlags",
        "require_approval": "requireApproval",
        "watch_excludes": "watchExcludes",
        "watch_includes": "watchIncludes",
        "cdk_version": "cdkVersion",
        "cdk_assert": "cdkAssert",
        "cdk_assertions": "cdkAssertions",
        "cdk_dependencies": "cdkDependencies",
        "cdk_dependencies_as_deps": "cdkDependenciesAsDeps",
        "cdk_test_dependencies": "cdkTestDependencies",
        "cdk_version_pinning": "cdkVersionPinning",
        "constructs_version": "constructsVersion",
        "app_entrypoint": "appEntrypoint",
        "integration_test_auto_discover": "integrationTestAutoDiscover",
        "lambda_auto_discover": "lambdaAutoDiscover",
        "lambda_options": "lambdaOptions",
    },
)
class PDKPipelineTsProjectOptions(projen.awscdk.AwsCdkTypeScriptAppOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[projen.javascript.CodeArtifactOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.javascript.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.javascript.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.javascript.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[projen.release.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_projen_upgrades: typing.Optional[builtins.bool] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[projen.github.workflows.Triggers] = None,
        bundler_options: typing.Optional[projen.javascript.BundlerOptions] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[projen.javascript.UpgradeDependenciesOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.javascript.JestOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[projen.javascript.PrettierOptions] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_upgrade_auto_merge: typing.Optional[builtins.bool] = None,
        projen_upgrade_schedule: typing.Optional[typing.Sequence[builtins.str]] = None,
        projen_upgrade_secret: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[typing.Any]] = None,
        workflow_git_identity: typing.Optional[projen.github.GitIdentity] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.javascript.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        build_command: typing.Optional[builtins.str] = None,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[projen.awscdk.ApprovalLevel] = None,
        watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version: builtins.str,
        cdk_assert: typing.Optional[builtins.bool] = None,
        cdk_assertions: typing.Optional[builtins.bool] = None,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
        cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version_pinning: typing.Optional[builtins.bool] = None,
        constructs_version: typing.Optional[builtins.str] = None,
        app_entrypoint: typing.Optional[builtins.str] = None,
        integration_test_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_auto_discover: typing.Optional[builtins.bool] = None,
        lambda_options: typing.Optional[projen.awscdk.LambdaFunctionCommonOptions] = None,
    ) -> None:
        '''Configuration options for the PDKPipelineTsProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_projen_upgrades: (experimental) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for depsUpgrade. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_upgrade_auto_merge: (deprecated) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: false
        :param projen_upgrade_schedule: (experimental) Customize the projenUpgrade schedule in cron expression. Default: [ "0 6 * * *" ]
        :param projen_upgrade_secret: (deprecated) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``). This setting is a GitHub secret name which contains a GitHub Access Token with ``repo`` and ``workflow`` permissions. This token is used to submit the upgrade pull request, which will likely include workflow updates. To create a personal access token see https://github.com/settings/tokens Default: - no automatic projen upgrade pull requests
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param build_command: (experimental) A command to execute before synthesis. This command will be called when running ``cdk synth`` or when ``cdk watch`` identifies a change in your source code before redeployment. Default: - no build command
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param watch_excludes: (experimental) Glob patterns to exclude from ``cdk watch``. Default: []
        :param watch_includes: (experimental) Glob patterns to include in ``cdk watch``. Default: []
        :param cdk_version: (experimental) Minimum version of the AWS CDK to depend on. Default: "2.1.0"
        :param cdk_assert: (deprecated) Warning: NodeJS only. Install the @aws-cdk/assert library? Default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0
        :param cdk_assertions: (experimental) Install the assertions library? Only needed for CDK 1.x. If using CDK 2.x then assertions is already included in 'aws-cdk-lib' Default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0
        :param cdk_dependencies: (deprecated) Which AWS CDKv1 modules this project requires.
        :param cdk_dependencies_as_deps: (deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``). This is to ensure that downstream consumers actually have your CDK dependencies installed when using npm < 7 or yarn, where peer dependencies are not automatically installed. If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure they are present during development. Note: this setting only applies to construct library projects Default: true
        :param cdk_test_dependencies: (deprecated) AWS CDK modules required for testing.
        :param cdk_version_pinning: (experimental) Use pinned version instead of caret version for CDK. You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates. If you use experimental features this will let you define the moment you include breaking changes.
        :param constructs_version: (experimental) Minimum version of the ``constructs`` library to depend on. Default: - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is "10.0.5".
        :param app_entrypoint: (experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default). Default: "main.ts"
        :param integration_test_auto_discover: (experimental) Automatically discovers and creates integration tests for each ``.integ.ts`` file in under your test directory. Default: true
        :param lambda_auto_discover: (experimental) Automatically adds an ``awscdk.LambdaFunction`` for each ``.lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project. Default: true
        :param lambda_options: (experimental) Common options for all AWS Lambda functions. Default: - default options
        '''
        if isinstance(logging, dict):
            logging = projen.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = projen.ProjenrcOptions(**projenrc_json_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = projen.github.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = projen.github.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = projen.github.GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = projen.github.MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = projen.SampleReadmeProps(**readme)
        if isinstance(stale_options, dict):
            stale_options = projen.github.StaleOptions(**stale_options)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = projen.javascript.CodeArtifactOptions(**code_artifact_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = projen.javascript.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = projen.github.workflows.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = projen.javascript.BundlerOptions(**bundler_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = projen.github.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = projen.javascript.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(jest_options, dict):
            jest_options = projen.javascript.JestOptions(**jest_options)
        if isinstance(prettier_options, dict):
            prettier_options = projen.javascript.PrettierOptions(**prettier_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = projen.javascript.ProjenrcOptions(**projenrc_js_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = projen.github.GitIdentity(**workflow_git_identity)
        if isinstance(eslint_options, dict):
            eslint_options = projen.javascript.EslintOptions(**eslint_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = projen.typescript.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(tsconfig, dict):
            tsconfig = projen.javascript.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = projen.javascript.TypescriptConfigOptions(**tsconfig_dev)
        if isinstance(lambda_options, dict):
            lambda_options = projen.awscdk.LambdaFunctionCommonOptions(**lambda_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "default_release_branch": default_release_branch,
            "cdk_version": cdk_version,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if bin is not None:
            self._values["bin"] = bin
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if deps is not None:
            self._values["deps"] = deps
        if description is not None:
            self._values["description"] = description
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if scripts is not None:
            self._values["scripts"] = scripts
        if stability is not None:
            self._values["stability"] = stability
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if auto_approve_projen_upgrades is not None:
            self._values["auto_approve_projen_upgrades"] = auto_approve_projen_upgrades
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if package is not None:
            self._values["package"] = package
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projen_upgrade_auto_merge is not None:
            self._values["projen_upgrade_auto_merge"] = projen_upgrade_auto_merge
        if projen_upgrade_schedule is not None:
            self._values["projen_upgrade_schedule"] = projen_upgrade_schedule
        if projen_upgrade_secret is not None:
            self._values["projen_upgrade_secret"] = projen_upgrade_secret
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if release is not None:
            self._values["release"] = release
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if libdir is not None:
            self._values["libdir"] = libdir
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if build_command is not None:
            self._values["build_command"] = build_command
        if cdkout is not None:
            self._values["cdkout"] = cdkout
        if context is not None:
            self._values["context"] = context
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if require_approval is not None:
            self._values["require_approval"] = require_approval
        if watch_excludes is not None:
            self._values["watch_excludes"] = watch_excludes
        if watch_includes is not None:
            self._values["watch_includes"] = watch_includes
        if cdk_assert is not None:
            self._values["cdk_assert"] = cdk_assert
        if cdk_assertions is not None:
            self._values["cdk_assertions"] = cdk_assertions
        if cdk_dependencies is not None:
            self._values["cdk_dependencies"] = cdk_dependencies
        if cdk_dependencies_as_deps is not None:
            self._values["cdk_dependencies_as_deps"] = cdk_dependencies_as_deps
        if cdk_test_dependencies is not None:
            self._values["cdk_test_dependencies"] = cdk_test_dependencies
        if cdk_version_pinning is not None:
            self._values["cdk_version_pinning"] = cdk_version_pinning
        if constructs_version is not None:
            self._values["constructs_version"] = constructs_version
        if app_entrypoint is not None:
            self._values["app_entrypoint"] = app_entrypoint
        if integration_test_auto_discover is not None:
            self._values["integration_test_auto_discover"] = integration_test_auto_discover
        if lambda_auto_discover is not None:
            self._values["lambda_auto_discover"] = lambda_auto_discover
        if lambda_options is not None:
            self._values["lambda_options"] = lambda_options

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[projen.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[projen.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[projen.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[projen.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[projen.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[projen.ProjenrcOptions], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[projen.github.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[projen.github.AutoApproveOptions], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[projen.github.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[projen.github.AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[projen.github.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[projen.github.GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[projen.github.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[projen.github.MergifyOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[projen.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[projen.ProjectType], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[projen.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[projen.SampleReadmeProps], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[projen.github.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[projen.github.StaleOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Author's Organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[projen.javascript.CodeArtifactOptions]:
        '''(experimental) Options for publishing npm package to AWS CodeArtifact.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[projen.javascript.CodeArtifactOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'express', 'lodash', 'foo@^2' ]
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'typescript', '@types/express' ]
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``).

        Set to an empty string to not include ``main`` in your package.json

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum node.js version to require via ``engines`` (inclusive).

        :default: - no max

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive).

        :default: - no "engines" specified

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[projen.javascript.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[projen.javascript.NpmAccess], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[projen.javascript.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[projen.javascript.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[projen.javascript.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[projen.javascript.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_trigger(self) -> typing.Optional[projen.release.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[projen.release.ReleaseTrigger], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with standard-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_release_branch(self) -> builtins.str:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        assert result is not None, "Required property 'default_release_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_projen_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_approve_projen_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[projen.github.workflows.Triggers]:
        '''(experimental) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[projen.github.workflows.Triggers], result)

    @builtins.property
    def bundler_options(self) -> typing.Optional[projen.javascript.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[projen.javascript.BundlerOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(self) -> typing.Optional[projen.github.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[projen.github.DependabotOptions], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[projen.javascript.UpgradeDependenciesOptions]:
        '''(experimental) Options for depsUpgrade.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[projen.javascript.UpgradeDependenciesOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[projen.javascript.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[projen.javascript.JestOptions], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(self) -> typing.Optional[projen.javascript.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[projen.javascript.PrettierOptions], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js_options(self) -> typing.Optional[projen.javascript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[projen.javascript.ProjenrcOptions], result)

    @builtins.property
    def projen_upgrade_auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically approve projen upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: false

        :deprecated: use ``autoApproveProjenUpgrades``.

        :stability: deprecated
        '''
        result = self._values.get("projen_upgrade_auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projen_upgrade_schedule(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Customize the projenUpgrade schedule in cron expression.

        :default: [ "0 6 * * *" ]

        :stability: experimental
        '''
        result = self._values.get("projen_upgrade_schedule")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def projen_upgrade_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Periodically submits a pull request for projen upgrades (executes ``yarn projen:upgrade``).

        This setting is a GitHub secret name which contains a GitHub Access Token
        with ``repo`` and ``workflow`` permissions.

        This token is used to submit the upgrade pull request, which will likely
        include workflow updates.

        To create a personal access token see https://github.com/settings/tokens

        :default: - no automatic projen upgrade pull requests

        :deprecated: use ``githubTokenSecret`` instead.

        :stability: deprecated
        '''
        result = self._values.get("projen_upgrade_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_bootstrap_steps(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def workflow_git_identity(self) -> typing.Optional[projen.github.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[projen.github.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version to use in GitHub workflows.

        :default: - same as ``minNodeVersion``

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(self) -> typing.Optional[projen.javascript.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[projen.javascript.EslintOptions], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(self) -> typing.Optional[projen.typescript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[projen.typescript.ProjenrcOptions], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``.

        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(self) -> typing.Optional[projen.javascript.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[projen.javascript.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[projen.javascript.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[projen.javascript.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) A command to execute before synthesis.

        This command will be called when
        running ``cdk synth`` or when ``cdk watch`` identifies a change in your source
        code before redeployment.

        :default: - no build command

        :stability: experimental
        '''
        result = self._values.get("build_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdkout(self) -> typing.Optional[builtins.str]:
        '''(experimental) cdk.out directory.

        :default: "cdk.out"

        :stability: experimental
        '''
        result = self._values.get("cdkout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional context to include in ``cdk.json``.

        :default: - no additional context

        :stability: experimental
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include all feature flags in cdk.json.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[projen.awscdk.ApprovalLevel]:
        '''(experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them.

        :default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[projen.awscdk.ApprovalLevel], result)

    @builtins.property
    def watch_excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to exclude from ``cdk watch``.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("watch_excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def watch_includes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to include in ``cdk watch``.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("watch_includes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_version(self) -> builtins.str:
        '''(experimental) Minimum version of the AWS CDK to depend on.

        :default: "2.1.0"

        :stability: experimental
        '''
        result = self._values.get("cdk_version")
        assert result is not None, "Required property 'cdk_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdk_assert(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Warning: NodeJS only.

        Install the @aws-cdk/assert library?

        :default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0

        :deprecated: The

        :stability: deprecated
        :aws-cdk: /assertions (in V1) and included in ``aws-cdk-lib`` for V2.
        '''
        result = self._values.get("cdk_assert")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_assertions(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install the assertions library?

        Only needed for CDK 1.x. If using CDK 2.x then
        assertions is already included in 'aws-cdk-lib'

        :default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0

        :stability: experimental
        '''
        result = self._values.get("cdk_assertions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Which AWS CDKv1 modules this project requires.

        :deprecated: For CDK 2.x use "deps" instead. (or "peerDeps" if you're building a library)

        :stability: deprecated
        '''
        result = self._values.get("cdk_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_dependencies_as_deps(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``).

        This is to ensure that downstream consumers actually have your CDK dependencies installed
        when using npm < 7 or yarn, where peer dependencies are not automatically installed.
        If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure
        they are present during development.

        Note: this setting only applies to construct library projects

        :default: true

        :deprecated: Not supported in CDK v2.

        :stability: deprecated
        '''
        result = self._values.get("cdk_dependencies_as_deps")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cdk_test_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) AWS CDK modules required for testing.

        :deprecated: For CDK 2.x use 'devDeps' (in node.js projects) or 'testDeps' (in java projects) instead

        :stability: deprecated
        '''
        result = self._values.get("cdk_test_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_version_pinning(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pinned version instead of caret version for CDK.

        You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates.
        If you use experimental features this will let you define the moment you include breaking changes.

        :stability: experimental
        '''
        result = self._values.get("cdk_version_pinning")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def constructs_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum version of the ``constructs`` library to depend on.

        :default:

        - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is
        "10.0.5".

        :stability: experimental
        '''
        result = self._values.get("constructs_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default).

        :default: "main.ts"

        :stability: experimental
        '''
        result = self._values.get("app_entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_test_auto_discover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically discovers and creates integration tests for each ``.integ.ts`` file in under your test directory.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("integration_test_auto_discover")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_auto_discover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically adds an ``awscdk.LambdaFunction`` for each ``.lambda.ts`` handler in your source tree. If this is disabled, you can manually add an ``awscdk.AutoDiscover`` component to your project.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("lambda_auto_discover")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_options(
        self,
    ) -> typing.Optional[projen.awscdk.LambdaFunctionCommonOptions]:
        '''(experimental) Common options for all AWS Lambda functions.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("lambda_options")
        return typing.cast(typing.Optional[projen.awscdk.LambdaFunctionCommonOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PDKPipelineTsProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PdkPipelinePyProject(
    projen.awscdk.AwsCdkPythonApp,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-prototyping-sdk.pdk_projen.PdkPipelinePyProject",
):
    '''Synthesizes a Python Project with a CI/CD pipeline.

    :pjid: pdk-pipeline-py
    '''

    def __init__(
        self,
        *,
        app_entrypoint: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        module_name: builtins.str,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[projen.python.ProjenrcOptions] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[projen.python.PytestOptions] = None,
        sample: typing.Optional[builtins.bool] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional[projen.python.VenvOptions] = None,
        build_command: typing.Optional[builtins.str] = None,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[projen.awscdk.ApprovalLevel] = None,
        watch_excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        watch_includes: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version: builtins.str,
        cdk_assert: typing.Optional[builtins.bool] = None,
        cdk_assertions: typing.Optional[builtins.bool] = None,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_dependencies_as_deps: typing.Optional[builtins.bool] = None,
        cdk_test_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_version_pinning: typing.Optional[builtins.bool] = None,
        constructs_version: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
    ) -> None:
        '''
        :param app_entrypoint: (experimental) The CDK app's entrypoint (relative to the source directory, which is "src" by default). Default: "app.py"
        :param testdir: (experimental) Python sources directory. Default: "tests"
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: true
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. Default: false
        :param projenrc_python: (experimental) Use projenrc in python. This will install ``projen`` as a python dependency and will add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true if the project type is library
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: true
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param build_command: (experimental) A command to execute before synthesis. This command will be called when running ``cdk synth`` or when ``cdk watch`` identifies a change in your source code before redeployment. Default: - no build command
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param watch_excludes: (experimental) Glob patterns to exclude from ``cdk watch``. Default: []
        :param watch_includes: (experimental) Glob patterns to include in ``cdk watch``. Default: []
        :param cdk_version: (experimental) Minimum version of the AWS CDK to depend on. Default: "2.1.0"
        :param cdk_assert: (deprecated) Warning: NodeJS only. Install the @aws-cdk/assert library? Default: - will be included by default for AWS CDK >= 1.0.0 < 2.0.0
        :param cdk_assertions: (experimental) Install the assertions library? Only needed for CDK 1.x. If using CDK 2.x then assertions is already included in 'aws-cdk-lib' Default: - will be included by default for AWS CDK >= 1.111.0 < 2.0.0
        :param cdk_dependencies: (deprecated) Which AWS CDKv1 modules this project requires.
        :param cdk_dependencies_as_deps: (deprecated) If this is enabled (default), all modules declared in ``cdkDependencies`` will be also added as normal ``dependencies`` (as well as ``peerDependencies``). This is to ensure that downstream consumers actually have your CDK dependencies installed when using npm < 7 or yarn, where peer dependencies are not automatically installed. If this is disabled, ``cdkDependencies`` will be added to ``devDependencies`` to ensure they are present during development. Note: this setting only applies to construct library projects Default: true
        :param cdk_test_dependencies: (deprecated) AWS CDK modules required for testing.
        :param cdk_version_pinning: (experimental) Use pinned version instead of caret version for CDK. You can use this to prevent mixed versions for your CDK dependencies and to prevent auto-updates. If you use experimental features this will let you define the moment you include breaking changes.
        :param constructs_version: (experimental) Minimum version of the ``constructs`` library to depend on. Default: - for CDK 1.x the default is "3.2.27", for CDK 2.x the default is "10.0.5".
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        '''
        options = PDKPipelinePyProjectOptions(
            app_entrypoint=app_entrypoint,
            testdir=testdir,
            module_name=module_name,
            deps=deps,
            dev_deps=dev_deps,
            pip=pip,
            poetry=poetry,
            projenrc_python=projenrc_python,
            projenrc_python_options=projenrc_python_options,
            pytest=pytest,
            pytest_options=pytest_options,
            sample=sample,
            setuptools=setuptools,
            venv=venv,
            venv_options=venv_options,
            build_command=build_command,
            cdkout=cdkout,
            context=context,
            feature_flags=feature_flags,
            require_approval=require_approval,
            watch_excludes=watch_excludes,
            watch_includes=watch_includes,
            cdk_version=cdk_version,
            cdk_assert=cdk_assert,
            cdk_assertions=cdk_assertions,
            cdk_dependencies=cdk_dependencies,
            cdk_dependencies_as_deps=cdk_dependencies_as_deps,
            cdk_test_dependencies=cdk_test_dependencies,
            cdk_version_pinning=cdk_version_pinning,
            constructs_version=constructs_version,
            auto_approve_options=auto_approve_options,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            author_email=author_email,
            author_name=author_name,
            version=version,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            license=license,
            poetry_options=poetry_options,
            setup_config=setup_config,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
        )

        jsii.create(self.__class__, self, [options])


@jsii.enum(jsii_type="aws-prototyping-sdk.pdk_projen.SampleLanguage")
class SampleLanguage(enum.Enum):
    '''Supported languages to generate sample code.'''

    TYPESCRIPT = "TYPESCRIPT"
    PYTHON = "PYTHON"


@jsii.data_type(
    jsii_type="aws-prototyping-sdk.pdk_projen.TargetDependency",
    jsii_struct_bases=[],
    name_mapping={"projects": "projects", "target": "target"},
)
class TargetDependency:
    def __init__(
        self,
        *,
        projects: "TargetDependencyProject",
        target: builtins.str,
    ) -> None:
        '''Represents an NX Target Dependency.

        :param projects: Target dependencies.
        :param target: Projen target i.e: build, test, etc.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "projects": projects,
            "target": target,
        }

    @builtins.property
    def projects(self) -> "TargetDependencyProject":
        '''Target dependencies.'''
        result = self._values.get("projects")
        assert result is not None, "Required property 'projects' is missing"
        return typing.cast("TargetDependencyProject", result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Projen target i.e: build, test, etc.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetDependency(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="aws-prototyping-sdk.pdk_projen.TargetDependencyProject")
class TargetDependencyProject(enum.Enum):
    '''Supported enums for a TargetDependency.'''

    SELF = "SELF"
    '''Only rely on the package where the target is called.

    This is usually done for test like targets where you only want to run unit
    tests on the target packages without testing all dependent packages.
    '''
    DEPENDENCIES = "DEPENDENCIES"
    '''Target relies on executing the target against all dependencies first.

    This is usually done for build like targets where you want to build all
    dependant projects first.
    '''


__all__ = [
    "NxMonorepoProject",
    "NxMonorepoProjectOptions",
    "PDKPipelinePyProjectOptions",
    "PDKPipelineTsProject",
    "PDKPipelineTsProjectOptions",
    "PdkPipelinePyProject",
    "SampleLanguage",
    "TargetDependency",
    "TargetDependencyProject",
]

publication.publish()
