# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.5.11](https://github.com/cpenv/cpenv/releases/tag/0.5.11) - 2020-08-11

<small>[Compare with 0.5.10](https://github.com/cpenv/cpenv/compare/0.5.10...0.5.11)</small>

### Added
- Add: support for four decimal versions ([231fbdb](https://github.com/cpenv/cpenv/commit/231fbdbd4ec171fa1df4cb4d3d647601956ec046) by Dan Bradham).

### Changed
- Change: rename module.as_spec to module.to_spec ([c751275](https://github.com/cpenv/cpenv/commit/c751275d840f3e1c2054da570f1a5aaf68e65ae4) by Dan Bradham).

### Fixed
- Fix: circular imports caused issue in py2.7 ([48da984](https://github.com/cpenv/cpenv/commit/48da984ea5adc469f00226e291b9836b3863af2b) by Dan Bradham).


## [0.5.10](https://github.com/cpenv/cpenv/releases/tag/0.5.10) - 2020-08-08

<small>[Compare with 0.5.9](https://github.com/cpenv/cpenv/compare/0.5.9...0.5.10)</small>

### Added
- Add: warning at cli when cpenv is not up-to-date. closes #23. ([e27b0fd](https://github.com/cpenv/cpenv/commit/e27b0fddf02f7d74ae50cd2df566dd489a293e09) by Dan Bradham).


## [0.5.9](https://github.com/cpenv/cpenv/releases/tag/0.5.9) - 2020-08-07

<small>[Compare with 0.5.8](https://github.com/cpenv/cpenv/compare/0.5.8...0.5.9)</small>

### Fixed
- Fix: #22 .git folders excluded when publishing to a shotgunrepo ([ea00b98](https://github.com/cpenv/cpenv/commit/ea00b98b96de3c61692122466836e9fbcd9680f6) by Dan Bradham).


## [0.5.8](https://github.com/cpenv/cpenv/releases/tag/0.5.8) - 2020-08-06

<small>[Compare with 0.5.7](https://github.com/cpenv/cpenv/compare/0.5.7...0.5.8)</small>

### Changed
- Change: update changelog.md ([ae4d624](https://github.com/cpenv/cpenv/commit/ae4d624143442d326493814c9b1e513911866dea) by Dan Bradham).
- Change: bump version to 0.5.8 ([3d56640](https://github.com/cpenv/cpenv/commit/3d566401c47e04d0ae6e2761ab6e07c9ab32187d) by Dan Bradham).
- Change: update readme.md ([916fccf](https://github.com/cpenv/cpenv/commit/916fccf6ccfd2ea6f8d95f9317336d3302983472) by Dan Bradham).

### Fixed
- Fix: module constructed without a repo could not be activated ([f72fe1d](https://github.com/cpenv/cpenv/commit/f72fe1da90364438636ca89b09de504746c16e70) by Dan Bradham).


## [0.5.7](https://github.com/cpenv/cpenv/releases/tag/0.5.7) - 2020-06-29

<small>[Compare with 0.5.6](https://github.com/cpenv/cpenv/compare/0.5.6...0.5.7)</small>

### Changed
- Change: bump version to 0.5.7 ([7593718](https://github.com/cpenv/cpenv/commit/7593718d44a1ae46c3333bc69b8e2a09163070a0) by Dan Bradham).

### Fixed
- Fix: error when missing platform key for environment variable ([7e2aa03](https://github.com/cpenv/cpenv/commit/7e2aa03b214b319076e599ccc88b109f0a47e2fc) by Dan Bradham).


## [0.5.6](https://github.com/cpenv/cpenv/releases/tag/0.5.6) - 2020-06-03

<small>[Compare with 0.5.5](https://github.com/cpenv/cpenv/compare/0.5.5...0.5.6)</small>

### Changed
- Change: bump version to 0.5.6 ([0196bde](https://github.com/cpenv/cpenv/commit/0196bde5fbbc0bd2c902bb89cbd6ef3572c78b7a) by Dan Bradham).

### Fixed
- Fix: ensure redirect resolver is called first ([d6d7dbc](https://github.com/cpenv/cpenv/commit/d6d7dbc4a44edef70f4f1b66256623941eb47390) by Dan Bradham).


## [0.5.5](https://github.com/cpenv/cpenv/releases/tag/0.5.5) - 2020-06-01

<small>[Compare with 0.5.4](https://github.com/cpenv/cpenv/compare/0.5.4...0.5.5)</small>

### Added
- Add: vendor readme ([8d4f64d](https://github.com/cpenv/cpenv/commit/8d4f64dd723064df98a4737203792ca2f3216b62) by Dan Bradham).
- Add: vendor shotgun_api3 ([c310f68](https://github.com/cpenv/cpenv/commit/c310f68100a86f4a441b83ecf08b8b15d4241b8a) by Dan Bradham).
- Add: vendor certifi ([0b9c955](https://github.com/cpenv/cpenv/commit/0b9c9557b108ffc9a518a09f34c055c90d3fa8ee) by Dan Bradham).

### Changed
- Change: bump version to 0.5.5 ([b7744b6](https://github.com/cpenv/cpenv/commit/b7744b628e7675f4a6aa9b7b6973f03d3e26d6ba) by Dan Bradham).


## [0.5.4](https://github.com/cpenv/cpenv/releases/tag/0.5.4) - 2020-05-26

<small>[Compare with 0.5.3](https://github.com/cpenv/cpenv/compare/0.5.3...0.5.4)</small>

### Changed
- Change: bump version to 0.5.4 ([7a8235f](https://github.com/cpenv/cpenv/commit/7a8235f24eefbef31f590df3e6a4a9bac6c7f1c8) by Dan Bradham).

### Fixed
- Fix: explicitly set ssl certfile ([6758e90](https://github.com/cpenv/cpenv/commit/6758e903f15d3bcc5c8625d2d6779164f07b537b) by Dan Bradham).


## [0.5.3](https://github.com/cpenv/cpenv/releases/tag/0.5.3) - 2020-05-26

<small>[Compare with 0.5.2](https://github.com/cpenv/cpenv/compare/0.5.2...0.5.3)</small>

### Changed
- Change: bump version to 0.5.3 ([3fa6d4c](https://github.com/cpenv/cpenv/commit/3fa6d4cde0dcad66e566e270906ebf8e16a16c44) by Dan Bradham).
- Change: order of lookup in resolver docstrin ([0d33ec8](https://github.com/cpenv/cpenv/commit/0d33ec889a5ee6118282d7833dcf9e30a4dc12d6) by Dan Bradham).
- Change: switch to markdown for readme ([e318df0](https://github.com/cpenv/cpenv/commit/e318df050d0ad4c25b10dc46e14b6da114b8c65d) by Dan Bradham).
- Change: start rewriting readme ([7b639cd](https://github.com/cpenv/cpenv/commit/7b639cd6785f7da196f55f903407ad32da777093) by Dan Bradham).

### Fixed
- Fix: repo cache not cleared after localize/copy add: vendor cachetools ([127708d](https://github.com/cpenv/cpenv/commit/127708d87ed07303c5aaf0e17846400453846010) by Dan Bradham).
- Fix subshells ([26e7a5b](https://github.com/cpenv/cpenv/commit/26e7a5be7d1f7757879c28e99463fc1f9598561e) by Dan Bradham).


## [0.5.2](https://github.com/cpenv/cpenv/releases/tag/0.5.2) - 2020-05-18

<small>[Compare with 0.5.1](https://github.com/cpenv/cpenv/compare/0.5.1...0.5.2)</small>

### Added
- Add: edit command - to open a module in a text editor ([baea3de](https://github.com/cpenv/cpenv/commit/baea3deaa89a51100cdfb763176f89331e88b379) by Dan Bradham).
- Add: clireporter with progress bars via tqdm ([abe8489](https://github.com/cpenv/cpenv/commit/abe848976f4e2587bdc016efd4ef3985c583e706) by Dan Bradham).
- Add: reporter module to provide an interface to progress reporting ([a2af264](https://github.com/cpenv/cpenv/commit/a2af264edb7f8bcea743ba96519395c9483e3b35) by Dan Bradham).
- Add: repo.get_size and get_thumbnail methods ([99cfb1b](https://github.com/cpenv/cpenv/commit/99cfb1b34592e790779dd1b8dbaf91c9d377603d) by Dan Bradham).

### Changed
- Change: bump version to 0.5.2 ([028023a](https://github.com/cpenv/cpenv/commit/028023aa7540a0c8e38ae55accb6292e7d29187e) by Dan Bradham).
- Change: report download and upload progress in localrepo ([d3581e1](https://github.com/cpenv/cpenv/commit/d3581e1e5ea770336e23a9f47b67c005357dd7c0) by Dan Bradham).
- Change: report download and upload progress in shotgunrepo ([82525dd](https://github.com/cpenv/cpenv/commit/82525ddedfd2ce9dde6ca820c2c737ea06c94987) by Dan Bradham).
- Change: report progress of resolver and localizer ([a3d56de](https://github.com/cpenv/cpenv/commit/a3d56de51ce5a90a33b040572f2ad832e7bed625) by Dan Bradham).


## [0.5.1](https://github.com/cpenv/cpenv/releases/tag/0.5.1) - 2020-05-11

<small>[Compare with 0.5.0](https://github.com/cpenv/cpenv/compare/0.5.0...0.5.1)</small>

### Changed
- Change: bump version to 0.5.1 ([3d697d9](https://github.com/cpenv/cpenv/commit/3d697d90961e53434395ae19b8a665695827cf12) by Dan Bradham).

### Fixed
- Fix: cli entry point ([3835536](https://github.com/cpenv/cpenv/commit/3835536456b303ef146a4c4f20238fbd980a0399) by Dan Bradham).

### Removed
- Remove: shotgun-api3 from dependencies ([858d927](https://github.com/cpenv/cpenv/commit/858d92746879a02444ffaf1e0b51bbb34f12bbbc) by Dan Bradham).


## [0.5.0](https://github.com/cpenv/cpenv/releases/tag/0.5.0) - 2020-05-11

<small>[Compare with 0.4.4](https://github.com/cpenv/cpenv/compare/0.4.4...0.5.0)</small>

### Added
- Add: vendor.requests - imports requests from local site or pip._vendor ([17a6d16](https://github.com/cpenv/cpenv/commit/17a6d16f5700783d8ccd0386019e15cc74f2933f) by Dan Bradham).
- Add: support for nuke style versioning (yuck) ([69271db](https://github.com/cpenv/cpenv/commit/69271db320410b038730900ae716ecd19fe737ed) by Dan Bradham).
- Add: icon support ([a0fb55d](https://github.com/cpenv/cpenv/commit/a0fb55d6dc330ad377427f6b85bb78fa1e716bda) by Dan Bradham).
- Add: method repo.get_data ([c9e068a](https://github.com/cpenv/cpenv/commit/c9e068ab73954b4eaef566aa52cdedadec6ef474) by Dan Bradham).
- Add: changelog ([3d02bd0](https://github.com/cpenv/cpenv/commit/3d02bd023f498a551ae5f6c0d4a64a370742a0a1) by Dan Bradham).
- Add: more tests for localrepo ([17659c3](https://github.com/cpenv/cpenv/commit/17659c3f8b922502c1c653821ae7063a6950678a) by Dan Bradham).
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
- Change: split utils into paths and mappings modules ([aeeb4fd](https://github.com/cpenv/cpenv/commit/aeeb4fd1a8d0af983b2626c89e9eb543a40aaa08) by Dan Bradham).
- Change: shotgunrepo uploads full config to a new sg_data field. ([7666c22](https://github.com/cpenv/cpenv/commit/7666c2239253183630f7ff3590575b574adeb224) by Dan Bradham).
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
- Fix: get_cache_path redeclared "paths" module ([5abf6e2](https://github.com/cpenv/cpenv/commit/5abf6e227866ef6aa2180d07b2ed71c767baa9d0) by Dan Bradham).
- Fix: import deps in __init__ ([3b39117](https://github.com/cpenv/cpenv/commit/3b39117c2b4de466c314230dda0fbc8657bd7444) by Dan Bradham).
- Fix: _init failed when repo construction raised ([c81dd34](https://github.com/cpenv/cpenv/commit/c81dd349bebef31ace1b9cc8b55b8709af582e9a) by Dan Bradham).
- Fix: py27 compatability issues ([15d68b1](https://github.com/cpenv/cpenv/commit/15d68b1808b6e840729dfcf80956b37d7129928e) by Dan Bradham).
- Fix: module.run_hook did not return hooks result ([f24dd26](https://github.com/cpenv/cpenv/commit/f24dd26bf7ba51d45791ea7904b368cde7ee8250) by Dan Bradham).
- Fix: nameerror in localizer ([327cb39](https://github.com/cpenv/cpenv/commit/327cb390c711a8aea883c0a00a3feb21001f8c2b) by Dan Bradham).
- Fix: copier failed when to_repo was not a localrepo ([5dad1fc](https://github.com/cpenv/cpenv/commit/5dad1fc09434b5ac99b39ca1fa231688b17fb459) by Dan Bradham).
- Fix: spacing in __main__ ([d058c1d](https://github.com/cpenv/cpenv/commit/d058c1da2e057c044fb0750e16a82ddcbf85ec58) by Dan Bradham).
- Fix: resolver tests broken by refactoring ([82c5226](https://github.com/cpenv/cpenv/commit/82c52269b194d45545b744b9c7c3d918ccedcd96) by Dan Bradham).
- Fix: localrepo in tests requires name param ([98e8419](https://github.com/cpenv/cpenv/commit/98e8419911d46390b4b989fb3516cb4698b81964) by Dan Bradham).
- Fix formatting ([5a5108e](https://github.com/cpenv/cpenv/commit/5a5108ebd0623576c9616acaed26f2a734d60514) by Dan Bradham).
- Fix multiline resolver ([83f522e](https://github.com/cpenv/cpenv/commit/83f522ebd3045507be8ea589d8ec048ea3ac0ca0) by Dan Bradham).

### Removed
- Remove: hooks docstring ([5690105](https://github.com/cpenv/cpenv/commit/56901053503a3fb7e6c8dcaa4af9f06c9508c02a) by Dan Bradham).
- Remove: deps package ([76f26fb](https://github.com/cpenv/cpenv/commit/76f26fb63084c8b759a9951abbc2a1d41dc5ac01) by Dan Bradham).
- Remove: defaults.py ([f703f7c](https://github.com/cpenv/cpenv/commit/f703f7c5850e55f652d8baba2dd7bc741bf319ce) by Dan Bradham).
- Remove: log module remove: logging from deps ([91f8465](https://github.com/cpenv/cpenv/commit/91f8465653efb9a1d0d901f948fefd66283c935c) by Dan Bradham).
- Remove: setuptools files ([1fe45f5](https://github.com/cpenv/cpenv/commit/1fe45f5e47bb2e11d1b2590bbe0185f96690406e) by Dan Bradham).
- Remove environmentcache ([86f85c1](https://github.com/cpenv/cpenv/commit/86f85c16d839e97820ec34074a66c03a82290072) by Dan Bradham).


## [0.4.4](https://github.com/cpenv/cpenv/releases/tag/0.4.4) - 2019-10-30

<small>[Compare with 0.4.3](https://github.com/cpenv/cpenv/compare/0.4.3...0.4.4)</small>


## [0.4.3](https://github.com/cpenv/cpenv/releases/tag/0.4.3) - 2019-09-18

<small>[Compare with 0.4.2](https://github.com/cpenv/cpenv/compare/0.4.2...0.4.3)</small>

### Added
- Add wheel dev dep ([160e371](https://github.com/cpenv/cpenv/commit/160e371186c213693175163337d7317a924f2030) by Dan Bradham).

### Removed
- Remove vendor packages ([f8640dc](https://github.com/cpenv/cpenv/commit/f8640dc771dd45d641dbad7ba316b1a1e0681c70) by Dan Bradham).


## [0.4.2](https://github.com/cpenv/cpenv/releases/tag/0.4.2) - 2019-07-25

<small>[Compare with 0.4.1](https://github.com/cpenv/cpenv/compare/0.4.1...0.4.2)</small>

### Fixed
- Fix mockgit ([afbb569](https://github.com/cpenv/cpenv/commit/afbb569ae04002743db041d3629a5be8c290bd89) by Dan Bradham).


## [0.4.1](https://github.com/cpenv/cpenv/releases/tag/0.4.1) - 2017-10-12

<small>[Compare with 0.4.0](https://github.com/cpenv/cpenv/compare/0.4.0...0.4.1)</small>


## [0.4.0](https://github.com/cpenv/cpenv/releases/tag/0.4.0) - 2017-08-23

<small>[Compare with first commit](https://github.com/cpenv/cpenv/compare/817088dd9695b74593ecf3a89d84fc7f29aea0c8...0.4.0)</small>

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


