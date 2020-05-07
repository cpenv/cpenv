# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.5.0](https://github.com/cpenv/cpenv/releases/tag/0.5.0) ([compare](https://github.com/cpenv/cpenv/compare/0.4.4...0.5.0))

### Added
- Add: shotgun_api3 to dev dependencies ([df4fe08](https://github.com/cpenv/cpenv/commit/df4fe08ea34536a8a690ce63d7b34a82e04c16bb) by Dan Bradham).
- Add: shotgunrepo - supports storing modules directly in the sg database ([53f5cfc](https://github.com/cpenv/cpenv/commit/53f5cfcf8bbeed368eb72587b68d107bb6433c4e) by Dan Bradham).
- Add: properties to module ([4ff9cb4](https://github.com/cpenv/cpenv/commit/4ff9cb49de9986dcfda025d0ce602c330479b953) by Dan Bradham).
- Add: cli.safe_eval - uses ast.literal_eval to safely eval strings ([7fa8ca8](https://github.com/cpenv/cpenv/commit/7fa8ca8d118c3d8c03f003a9b23cb9857acd1f9c) by Dan Bradham).
- Add: config methods to api - get_config_path - returns path to config file - read_config - read the config or one config key - write_config - write the config or one config key ([1b37061](https://github.com/cpenv/cpenv/commit/1b37061cad05ac5f26b4532ee796fe0ba59b7271) by Dan Bradham).
- Add: cli repo add and remove commands these commands allow users to configure repos without dealing with configuration files ([2827cbd](https://github.com/cpenv/cpenv/commit/2827cbd7b80061f58547e098707b8eddd3188c58) by Dan Bradham).
- Add: info cli command - displays metadata for resolved modules ([0215568](https://github.com/cpenv/cpenv/commit/02155689a8f4eccf165c0995fce01b2bc827ba77) by Dan Bradham).
- Add: repos.registry for storing available repo subclasses ([d578653](https://github.com/cpenv/cpenv/commit/d578653e00edfcad335c10b84fec030f235fceaf) by Dan Bradham).
- Add: __str__ method to version and modulespec ([333a580](https://github.com/cpenv/cpenv/commit/333a580f581b1fc2467df4fa9bf1fa219992195a) by Dan Bradham).
- Add: type_name attribute to repo ([da959c3](https://github.com/cpenv/cpenv/commit/da959c3bcc5f9c709b6a05d32880e1d87b455e30) by Dan Bradham).
- Add: repo cli command ([5aa4fbc](https://github.com/cpenv/cpenv/commit/5aa4fbc5436536c5c00874cf486dd6ce506c7bd8) by Dan Bradham).
- Add: requirement matching to module.py ([956c549](https://github.com/cpenv/cpenv/commit/956c5493462cacf0dafda011c1c7d3e55eb823f3) by Dan Bradham).
- Add: name attribute to repo ([491097e](https://github.com/cpenv/cpenv/commit/491097e4988f5364a0cbd746bc0606ede797e916) by Dan Bradham).
- Add: implement clone ([8f64b08](https://github.com/cpenv/cpenv/commit/8f64b080530e70ae341f25a04bce65f0505f008d) by Dan Bradham).
- Add: implement module publishing ([23dea62](https://github.com/cpenv/cpenv/commit/23dea62050ff0c429fadd27627c6371c7c9aadbc) by Dan Bradham).
- Add: implement module removal ([449a973](https://github.com/cpenv/cpenv/commit/449a9731fcf47b982f9a7ad4f37ce6ed18318b88) by Dan Bradham).
- Add: implement module localization ([aa2d4ef](https://github.com/cpenv/cpenv/commit/aa2d4ef0e84aeeeef4cb65a97afedb740fa89e9a) by Dan Bradham).
- Add: cli.echo and improve error reporting ([70c93c7](https://github.com/cpenv/cpenv/commit/70c93c7b9fb68e18720d0e7ad9f3ec61367b643f) by Dan Bradham).
- Add: more attrs to module object - qualified_name: name + '-' + version - real_name: basename of module directory or qualified_name ([7547d3c](https://github.com/cpenv/cpenv/commit/7547d3c62cdb367316ea98d8a0eaab2ff5c7748a) by Dan Bradham).
- Add: repo registry to api change: further flesh out repo object ([bf0b7cd](https://github.com/cpenv/cpenv/commit/bf0b7cd8c642a2cf3baae76f7626ee047bbf1aba) by Dan Bradham).
- Add: stub out api clone and publish methods ([cdd3867](https://github.com/cpenv/cpenv/commit/cdd3867ce922c9f0dd65c3d6b14ab55e594d11c3) by Dan Bradham).
- Add: repo register and unregister api methods ([8accbce](https://github.com/cpenv/cpenv/commit/8accbce5db3f9158b32577557fa07e31f9716798) by Dan Bradham).
- Add: create cli command ([6bad486](https://github.com/cpenv/cpenv/commit/6bad486224a5f96bbeab74fb97d53f5f437bfcde) by Dan Bradham).
- Add: repo object to handle finding and transferring modules ([c2b0d24](https://github.com/cpenv/cpenv/commit/c2b0d242238059b5f699b7616393c7ab29e55313) by Dan Bradham).
- Add: vendor appdirs.py ([2c71ba1](https://github.com/cpenv/cpenv/commit/2c71ba191f98cc803236eb4079de79e13784e23b) by Dan Bradham).
- Add: versions module to parse module versions ([4e2b03d](https://github.com/cpenv/cpenv/commit/4e2b03dc681599aa09a4de8fc5fcc2afa16d04a0) by Dan Bradham).
- Add: isort ([3d5a056](https://github.com/cpenv/cpenv/commit/3d5a056760428338e1df937c7066796e1ce3242e) by Dan Bradham).
- Add: pyproject.toml ([7264220](https://github.com/cpenv/cpenv/commit/726422030d7ac73cd331ee53185d7f0f5cb143f3) by Dan Bradham).
- Add mock dev dep ([8b67c8c](https://github.com/cpenv/cpenv/commit/8b67c8cb7bdcb0c351d7e23b02cb2aa1f09fddde) by Dan Bradham).

### Changed
- Change: update api and cli to use refined resolver ([a0d28cc](https://github.com/cpenv/cpenv/commit/a0d28cc196672b90e25a64d1d4862a024f1745c8) by Dan Bradham).
- Change: break up resolver into multiple classes - resolver: resolves requirements - activator: activates modules - localizer: downloads modules to local repos - copier: copies modules from one repo to another ([10b4259](https://github.com/cpenv/cpenv/commit/10b42595a4d93d31fb7d3356eeab97032e86d072) by Dan Bradham).
- Change: make repos registry an ordereddict rather than list ([9bc2f87](https://github.com/cpenv/cpenv/commit/9bc2f874cdc00759d4ab29f3ae5d93d5e50b30cb) by Dan Bradham).
- Change: refine repo interface - update localrepo to match ([5e76271](https://github.com/cpenv/cpenv/commit/5e762710adc120cdd0d59b3b9d5b7a70e1ba8dc5) by Dan Bradham).
- Change: improve and reorganize cli ([2c22594](https://github.com/cpenv/cpenv/commit/2c22594a228aaedfa24d468ce16431b2809e2715) by Dan Bradham).
- Change: refactor resolver to make use of new repo objects ([0275b50](https://github.com/cpenv/cpenv/commit/0275b50fcfc482288e72b7a2d40d59eca7877458) by Dan Bradham).
- Change: move platform var to compat ([f1343a8](https://github.com/cpenv/cpenv/commit/f1343a811b7670768e8687dcbef08b287d04a2e6) by Dan Bradham).
- Change: rename members of versions module ([11b107f](https://github.com/cpenv/cpenv/commit/11b107f564895f1566a5ab810e39519b8660300c) by Dan Bradham).
- Change: refine api documentation ([3587a1f](https://github.com/cpenv/cpenv/commit/3587a1fa06f9623817ca500427c59e477fa9756b) by Dan Bradham).
- Change: use appdirs for standardized managing of site and user directories ([c666e41](https://github.com/cpenv/cpenv/commit/c666e418ad301c34c24b247f807500470cb60aeb) by Dan Bradham).
- Change: intelligently determine name and version at module creation ([5acb8e8](https://github.com/cpenv/cpenv/commit/5acb8e89efe5a4d423eb238e8938a917e92f3201) by Dan Bradham).
- Change: use integers for version.major, minor and patch ([8379e06](https://github.com/cpenv/cpenv/commit/8379e066b3433f95dcadca191326db79d978a01b) by Dan Bradham).
- Change: update hook docs ([7561840](https://github.com/cpenv/cpenv/commit/7561840fc231209c06b263805303ab25f89711aa) by Dan Bradham).
- Change: move all config to pyproject.toml ([8dd3e9e](https://github.com/cpenv/cpenv/commit/8dd3e9ec43e992faf50dba8da298e7b58cb7b895) by Dan Bradham).
- Change: clean up shell.py ([34f3c7d](https://github.com/cpenv/cpenv/commit/34f3c7df047263b2bc489027fea290497b61ee01) by Dan Bradham).
- Change: remove concept of virtualenvironment ([0104bd3](https://github.com/cpenv/cpenv/commit/0104bd367ab73906c299ee167dc2eb917728650d) by Dan Bradham).
- Change: refactor api.create method ([3b28f77](https://github.com/cpenv/cpenv/commit/3b28f77814a503edffd071a569b71efd5b2680f5) by Dan Bradham).
- Change: update tests ([6f17776](https://github.com/cpenv/cpenv/commit/6f177769fee98dc30bd7a1650aaa536c43feaaf1) by Dan Bradham).
- Change: update pyproject.toml and poetry.lock ([5aea98c](https://github.com/cpenv/cpenv/commit/5aea98c5fc1a97bbe5d7b6abd20bc350a8d2cd03) by Dan Bradham).
- Change: remove some defunct docs ([d82e7ee](https://github.com/cpenv/cpenv/commit/d82e7ee3bbf18f3008dbd2746b4d6421cdcbbca3) by Dan Bradham).
- Change: rename models to module ([cfef8f7](https://github.com/cpenv/cpenv/commit/cfef8f71e60a7f91ad066f35cfb281ce0fd10fa2) by Dan Bradham).
- Change: refactor cli ([4c766d1](https://github.com/cpenv/cpenv/commit/4c766d148fb60ceeab0c841bac121bbaf4a37651) by Dan Bradham).
- Change: bump version to 0.5.0 ([998e5e5](https://github.com/cpenv/cpenv/commit/998e5e54f83c6f60dd291981b971e193a808f19c) by Dan Bradham).
- Change: vendor pyyaml ([f138973](https://github.com/cpenv/cpenv/commit/f138973443876e40c4d7064ecacf9570ec1f522f) by Dan Bradham).

### Fixed
- Fix: nameerror in localizer ([327cb39](https://github.com/cpenv/cpenv/commit/327cb390c711a8aea883c0a00a3feb21001f8c2b) by Dan Bradham).
- Fix: copier failed when to_repo was not a localrepo ([5dad1fc](https://github.com/cpenv/cpenv/commit/5dad1fc09434b5ac99b39ca1fa231688b17fb459) by Dan Bradham).
- Fix: spacing in __main__ ([d058c1d](https://github.com/cpenv/cpenv/commit/d058c1da2e057c044fb0750e16a82ddcbf85ec58) by Dan Bradham).
- Fix: resolver tests broken by refactoring ([82c5226](https://github.com/cpenv/cpenv/commit/82c52269b194d45545b744b9c7c3d918ccedcd96) by Dan Bradham).
- Fix: localrepo in tests requires name param ([98e8419](https://github.com/cpenv/cpenv/commit/98e8419911d46390b4b989fb3516cb4698b81964) by Dan Bradham).
- Fix formatting ([5a5108e](https://github.com/cpenv/cpenv/commit/5a5108ebd0623576c9616acaed26f2a734d60514) by Dan Bradham).
- Fix multiline resolver ([83f522e](https://github.com/cpenv/cpenv/commit/83f522ebd3045507be8ea589d8ec048ea3ac0ca0) by Dan Bradham).

### Removed
- Remove: defaults.py ([f703f7c](https://github.com/cpenv/cpenv/commit/f703f7c5850e55f652d8baba2dd7bc741bf319ce) by Dan Bradham).
- Remove: log module remove: logging from deps ([91f8465](https://github.com/cpenv/cpenv/commit/91f8465653efb9a1d0d901f948fefd66283c935c) by Dan Bradham).
- Remove: setuptools files ([1fe45f5](https://github.com/cpenv/cpenv/commit/1fe45f5e47bb2e11d1b2590bbe0185f96690406e) by Dan Bradham).
- Remove environmentcache ([86f85c1](https://github.com/cpenv/cpenv/commit/86f85c16d839e97820ec34074a66c03a82290072) by Dan Bradham).

### Misc
- Update: .gitignore ([2b745eb](https://github.com/cpenv/cpenv/commit/2b745eb9c26c5b03f2402c52c6df0223eb438e77) by Dan Bradham).
- Clarify get_module_paths ([417e716](https://github.com/cpenv/cpenv/commit/417e71650e3ea21945bcfc88ed63700010f83850) by Dan Bradham).
- Cli cosmetics ([bf2f075](https://github.com/cpenv/cpenv/commit/bf2f07540a22322bc986e26f8027fa2a72234663) by Dan Bradham).


## [0.4.4](https://github.com/cpenv/cpenv/releases/tag/0.4.4) ([compare](https://github.com/cpenv/cpenv/compare/0.4.3...0.4.4)) - 2019-10-30

### Misc
- Support multiline redirects ([ac4c607](https://github.com/cpenv/cpenv/commit/ac4c60711c27bcd5e1e1bbc850493af79ba7346a) by Dan Bradham).


## [0.4.3](https://github.com/cpenv/cpenv/releases/tag/0.4.3) ([compare](https://github.com/cpenv/cpenv/compare/0.4.2...0.4.3)) - 2019-09-18

### Added
- Add wheel dev dep ([160e371](https://github.com/cpenv/cpenv/commit/160e371186c213693175163337d7317a924f2030) by Dan Bradham).

### Removed
- Remove vendor packages ([f8640dc](https://github.com/cpenv/cpenv/commit/f8640dc771dd45d641dbad7ba316b1a1e0681c70) by Dan Bradham).


## [0.4.2](https://github.com/cpenv/cpenv/releases/tag/0.4.2) ([compare](https://github.com/cpenv/cpenv/compare/0.4.1...0.4.2)) - 2019-07-25

### Fixed
- Fix mockgit ([afbb569](https://github.com/cpenv/cpenv/commit/afbb569ae04002743db041d3629a5be8c290bd89) by Dan Bradham).

### Misc
- Update readme.rst and setup.py ([5dc74c6](https://github.com/cpenv/cpenv/commit/5dc74c68105cdb042eb2fc3abb3307eab5fe24c3) by Dan Bradham).
- Switch to yaml.safe_load ([d5b6f97](https://github.com/cpenv/cpenv/commit/d5b6f9720355809584b70fff598a922140d2bd66) by Dan Bradham).


## [0.4.1](https://github.com/cpenv/cpenv/releases/tag/0.4.1) ([compare](https://github.com/cpenv/cpenv/compare/0.4.0...0.4.1)) - 2017-10-12

### Misc
- Improved cli formatting ([8076d57](https://github.com/cpenv/cpenv/commit/8076d57fd7793e881d1fc86955a47ac7a86ffd64) by Dan Bradham).


## [0.4.0](https://github.com/cpenv/cpenv/releases/tag/0.4.0) ([compare](https://github.com/cpenv/cpenv/compare/817088dd9695b74593ecf3a89d84fc7f29aea0c8...0.4.0)) - 2017-08-23

### Added
- Add git requirement ([1dcbe8e](https://github.com/cpenv/cpenv/commit/1dcbe8e80f4c7219beeede2b7ba55421ab8445a8) by Dan Bradham).
- Added test coverage for redirect solver ([250de03](https://github.com/cpenv/cpenv/commit/250de035d61d00ca9ece39b93f47d39902a8a993) by Dan Bradham).
- Added redirect solver ([3e77469](https://github.com/cpenv/cpenv/commit/3e774692037f241ff79508fda668a5b2d0a98d09) by Dan Bradham).
- Add manifest.in ([cd63aca](https://github.com/cpenv/cpenv/commit/cd63aca42f0aa52c9da573f838424b7b9afea0f9) by Dan Bradham).
- Add: tests for hookfinder ([27c60fc](https://github.com/cpenv/cpenv/commit/27c60fc0976bb1b827307c0517e6e8f555f608a1) by Dan Bradham).
- Add: create using git repository as config change: module hooks now all end with "module". remove: a few redundant logging messages fix: prompt prefix now suffixed with active modules ([b6b152e](https://github.com/cpenv/cpenv/commit/b6b152eab22d5f31fc9ba4bdf8df66c6f92ba725) by Dan Bradham).
- Additional reporting ([468bfba](https://github.com/cpenv/cpenv/commit/468bfba55d980ffddcb5605b0ceb7997fd667253) by Dan Bradham).
- Added clear_cache flag to root cli. allows user to clear all cached environments not in cpenv_home path ([a1aca2e](https://github.com/cpenv/cpenv/commit/a1aca2e9059668d7c05a8f84bc96732416310edc) by Dan Bradham).
- Added additional documentation ([1b6177d](https://github.com/cpenv/cpenv/commit/1b6177da925ebde8aee530ab8922ab37d246590a) by Dan Bradham).

### Fixed
- Fix issue #9 ([4ac048a](https://github.com/cpenv/cpenv/commit/4ac048a5ba2118a85078b192f292799c4c339755) by Dan Bradham).
- Fix tables ([f7c1e11](https://github.com/cpenv/cpenv/commit/f7c1e1136aa78538b83ec5518ade4ceafc1d708a) by Dan Bradham).
- Fix issue #7: windows err on remove env and module ([9fe1f92](https://github.com/cpenv/cpenv/commit/9fe1f92c2fcfe371d3238af948b09679dfdeb927) by Dan Bradham).
- Fix bug where virtualenvironment.get_module would return a non-existing module\ngit clone is now recursive to support git submodules ([7f79129](https://github.com/cpenv/cpenv/commit/7f791293d9b2f6ab366979477f2dcccb064de904) by Dan Bradham).
- Fix cli launch printed after launching ([8897f8b](https://github.com/cpenv/cpenv/commit/8897f8bbc9c65e442e3877160ed3929bafca37ec) by Dan Bradham).
- Fixed regression with cpenv create ([e2b30b6](https://github.com/cpenv/cpenv/commit/e2b30b61b9451ba235b8d29ea6467b4a3fa6b8c6) by Dan Bradham).
- Fix: incorrect imports ([ffdc16b](https://github.com/cpenv/cpenv/commit/ffdc16bcbddce37d186007be8f758c8ea77263b6) by Dan Bradham).
- Fix: create environment using git repo config ([07d02b8](https://github.com/cpenv/cpenv/commit/07d02b886febe3984b8bb5fffb8b9f0b3ca4920c) by Dan Bradham).
- Fix: module upgrading ([935cdf7](https://github.com/cpenv/cpenv/commit/935cdf7b1548c7455971446eea5c8edd464ee451) by Dan Bradham).
- Fix: create using config add: virtualenvironment and module object resolvers change: dependencies section of config change: module config name to module.yml ([13aaca1](https://github.com/cpenv/cpenv/commit/13aaca1748f7b5e76f0debdeed4f97c72340f728) by Dan Bradham).
- Fixed regression in virtualenvironment.pip_update ([f7ba300](https://github.com/cpenv/cpenv/commit/f7ba30033771f6898d98029fe2ab5b7f9e653bb3) by Dan Bradham).
- Fix: full environment not being passed to new subshell, explicitly passing os.environ.data now ([9dc8102](https://github.com/cpenv/cpenv/commit/9dc8102f987664ee1acd391e1591970f2a93156d) by unknown).
- Fixed initialization of environmentcache ([c7d33db](https://github.com/cpenv/cpenv/commit/c7d33db42f970c8ca12c678d3d0a9a67d3c7cb9a) by Dan Bradham).
- Fix add_application_module ([4b51a46](https://github.com/cpenv/cpenv/commit/4b51a462fc3fe0164170f94f5f29a87b0d6c427f) by Dan Bradham).
- Fix: subshell launching on linux ([d20634d](https://github.com/cpenv/cpenv/commit/d20634dcebc10bf2053865d513d5c9df4cd5cf16) by Dan Bradham).

### Removed
- Remove navigation depth ([b1c03f6](https://github.com/cpenv/cpenv/commit/b1c03f6ae72e78c0de4c544f600f04f86cfeeec6) by Dan Bradham).
- Remove quickinstall scripts, add bdist_wheel support to setup.py ([77a5c69](https://github.com/cpenv/cpenv/commit/77a5c69fd56965fe532fc2b9522de89d021e374d) by Dan Bradham).

### Misc
- Couple of fixes to docs and tests ([1d0fec8](https://github.com/cpenv/cpenv/commit/1d0fec823f797701e9011e62ccf0b7778fab46ce) by Dan Bradham).
- Rewrite of cli ([22d5b4b](https://github.com/cpenv/cpenv/commit/22d5b4b556ad4d429120ab062016b0afb2491761) by Dan Bradham).
- Support modules outside python virtual envs ([fc9616b](https://github.com/cpenv/cpenv/commit/fc9616b08f70b27b7054e5113e666d798fe72de3) by Dan Bradham).
- Remcheese ([741ff4a](https://github.com/cpenv/cpenv/commit/741ff4aa6fd32efd40fb7d894379eac92e369481) by Dan Bradham).
- Version typo ([7df3051](https://github.com/cpenv/cpenv/commit/7df3051a77c06ed217862ed8099d33dd7ee11c43) by Dan Bradham).
- More next ([f15085a](https://github.com/cpenv/cpenv/commit/f15085a11f47002126411e01d246284af62f8223) by Dan Bradham).
- Whats next ([7c56897](https://github.com/cpenv/cpenv/commit/7c56897687f9a0a29cbdd9d8d55713dd2d3a1fc2) by Dan Bradham).
- Don't collapse nav ([79b173d](https://github.com/cpenv/cpenv/commit/79b173d5dc19828e4cf9086016778885fe1c4b34) by Dan Bradham).
- Mock virtualenv ([ecd0995](https://github.com/cpenv/cpenv/commit/ecd09952a1c0ce7233c1a35e1b012c7f43df0187) by Dan Bradham).
- Mock virtualenv in docs ([2e33be2](https://github.com/cpenv/cpenv/commit/2e33be281159cae82a53d75bb914109cedc652f2) by Dan Bradham).
- Moar documentation ([c571c34](https://github.com/cpenv/cpenv/commit/c571c341aa5d43220d23954012b6a738622fcbb0) by Dan Bradham).
- Explicitly set repo for python setup.py cheeseit! ([627d5d8](https://github.com/cpenv/cpenv/commit/627d5d8ea94bc3bdaa71330724d7ef668da2f8be) by Dan Bradham).
- No need to update pip or wheel after creating env ([333e2a3](https://github.com/cpenv/cpenv/commit/333e2a3902069bb80f5e33bcda9e9de771eb3cec) by Dan Bradham).
- Update readme.rst ([ef9dc3f](https://github.com/cpenv/cpenv/commit/ef9dc3fa0fcfa9d6135ca6b1367fc2a8e673f77e) by Dan Bradham).
- 0.2.35 ([4eac186](https://github.com/cpenv/cpenv/commit/4eac1869ffeb1852ca47ea04165241a3f775905a) by Dan Bradham).
- 0.2.24 ([7584991](https://github.com/cpenv/cpenv/commit/7584991a8dc1964f6454717b21ea46ca6fb4268e) by Dan Bradham).
- Pip 8.0 broken on windows ([3c05b1a](https://github.com/cpenv/cpenv/commit/3c05b1a445a461b2c1b395b8fbe265c3706c3e55) by Dan Bradham).
- Ensure cpenv_active_modules is bytes ([60d862b](https://github.com/cpenv/cpenv/commit/60d862b761676e90115efd8262e4c616cd0f114c) by Dan Bradham).
- 0.2.3 ([3cecabb](https://github.com/cpenv/cpenv/commit/3cecabbd9b7431f4d8bbf4299bbfa2f732ee696f) by Dan Bradham).
- 0.2.2 ([6fea02a](https://github.com/cpenv/cpenv/commit/6fea02ac70eb29f0c3cb6a39a714b284df22065f) by Dan Bradham).
- Update readme to reflect new terminology ([cfdf753](https://github.com/cpenv/cpenv/commit/cfdf753e42358420558695c470e0a289d1030241) by Dan Bradham).
- Hooks implementation ([b7e6332](https://github.com/cpenv/cpenv/commit/b7e633262e9c3eac28f07cbc231f0afcb1966990) by Dan Bradham).
- Fill out add_module method of virtualenvironment ([a0112c2](https://github.com/cpenv/cpenv/commit/a0112c2595537374903821ffdf66b8563f3406e1) by Dan Bradham).
- Overhauled api. better code organization. added compat, deps, and cache modules. moved envutils to utils ([2e6ee42](https://github.com/cpenv/cpenv/commit/2e6ee42cfbe5337dad50d582be25e657569b1411) by Dan Bradham).
- Resolver ([e1189c4](https://github.com/cpenv/cpenv/commit/e1189c4207737221665216b3310530472b5bc86d) by Dan Bradham).
- Resolved issue with pythonpath being overwritten on activation ([828b786](https://github.com/cpenv/cpenv/commit/828b786819b88002a64c5ec15dcf62b02134f21f) by Dan Bradham).
- Replacing os.environ.data doesn't actually set the env vars ([11fe8ef](https://github.com/cpenv/cpenv/commit/11fe8effdc6387bb0f93ba8f93a676a20cc62ce0) by Dan Bradham).
- Defer wheel management to pip.conf and user environment variables ([1c6803c](https://github.com/cpenv/cpenv/commit/1c6803cc355a1561fa0374015aae5065eb3de369) by Dan Bradham).
- Moved clear_cache flag to activate ([4dcb336](https://github.com/cpenv/cpenv/commit/4dcb3369d3c840f3d33e307b9864ab96e02cb842) by Dan Bradham).
- 0.1.10 ([c5556f6](https://github.com/cpenv/cpenv/commit/c5556f69982525eb3634d6a10614770083c548e1) by Dan Bradham).
- 0.1.9 ([1feacec](https://github.com/cpenv/cpenv/commit/1feacec39c364b9904f2f3fb70835b107719a27c) by Dan Bradham).
- 0.1.8 ([385bfd2](https://github.com/cpenv/cpenv/commit/385bfd26e771837bf487ceebf09fffa27efb23cd) by Dan Bradham).
- Improved wheel support: ([05a187d](https://github.com/cpenv/cpenv/commit/05a187d7ee1fdb9030cafcda2bae4654ec131287) by Dan Bradham).
- 0.1.6 fix: reversed args when installing an appmodule on create ([9ba6e66](https://github.com/cpenv/cpenv/commit/9ba6e66559d9a84b7c77f1dff84b070717ee3994) by unknown).
- Ensure unicode strings don't make their way into os.environ dict ([9e3fc26](https://github.com/cpenv/cpenv/commit/9e3fc265e54af08c26665defb6d0d65a1f45397d) by Dan Bradham).
- Import os ([7eaba85](https://github.com/cpenv/cpenv/commit/7eaba854764bd55bcdd3b03fbbdd74450a68c5be) by Dan Bradham).
- Updated readme and setup.py to support deployment to the cheeseshop ([e007983](https://github.com/cpenv/cpenv/commit/e007983e7086186571c6562ac17b3c27f7feb298) by Dan Bradham).
- Make sure envcache root path exists ([1b2e209](https://github.com/cpenv/cpenv/commit/1b2e20909650ea10fb6807e145e03a2dfe8be2b8) by Dan Bradham).
- Update version to 0.1.3 ([3e08c16](https://github.com/cpenv/cpenv/commit/3e08c16a3e8c7df363424fbe3c67ceac7e86a893) by unknown).
- Moved wheelhouse to root, moved envcache to user home ([b5d1afe](https://github.com/cpenv/cpenv/commit/b5d1afed4094f9776feb780e1c3dc27912cc9bf9) by unknown).
- Passing os.environ directly to new subshell ([1009ebd](https://github.com/cpenv/cpenv/commit/1009ebde6fa28ddcd4884d3d5e64752af911ea2d) by unknown).
- Force encoding utf8 ([8027476](https://github.com/cpenv/cpenv/commit/8027476d007148d46271b7e7119cf694513a24e6) by Dan Bradham).
- No more fudging with piping standard output to a batch or bash script. it was an interesting experiment but...launching subshells instead. this has huge benefits in terms of reducing clout and code complexity. ([b50970d](https://github.com/cpenv/cpenv/commit/b50970d08fa16153152e99511c0f21db7bd5da1b) by Dan Bradham).
- Rem: extraneous cli commands add: --module option to activate, create, and remove add: add_application_module method to virtualenvironment class add: get_application_module method to virtualenvironment class add: rem_application_module method to virtualenvironment class ([7d93f2b](https://github.com/cpenv/cpenv/commit/7d93f2b1c1a00e87929f8c03db3392a05faec69f) by Dan Bradham).
- Launchity launch launch update, use call instead of popen... ([734f827](https://github.com/cpenv/cpenv/commit/734f8274494e115df1e6c09e78ecb121e2311b13) by Dan Bradham).
- Working modules ([5a1607d](https://github.com/cpenv/cpenv/commit/5a1607d2656a7184c5e089717f591c0f7c484507) by Dan Bradham).
- Wooowee big improvements to api, no longer using virtualenv activate scripts, pure python goodness ([60a2697](https://github.com/cpenv/cpenv/commit/60a2697310bdbc754ed6ea64e999341f62454c3e) by Dan Bradham).
- Rewriting api in more object oriented style ([fd0adce](https://github.com/cpenv/cpenv/commit/fd0adce094580781270e4d19449da9f6a58dafe7) by Dan Bradham).
- Adjust activate/deactivate cli ([7d34252](https://github.com/cpenv/cpenv/commit/7d34252ab1c090b499806899d6a779b1be1e6262) by Dan Bradham).
- Initial commit ([817088d](https://github.com/cpenv/cpenv/commit/817088dd9695b74593ecf3a89d84fc7f29aea0c8) by Dan Bradham).


