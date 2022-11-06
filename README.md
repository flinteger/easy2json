# easylist2json

Convert EasyList to Safari content blocker list.

Note: content blockers are fairly limited. Hence, not all filters
can be converted (in a compatible way).

## Usage

```sh
node abp2blocklist.js < easylist.txt > blockerList.json
```

## Credit

- [abp2blocklist.js and related code from abp2blocklist](https://github.com/adblockplus/abp2blocklist.git)
- [EasyList](https://easylist.to/)

## License

- abp2blocklist.js and files in `lib` directory is the same as abp2blocklist: [GLP v3](LICENSE-GPLv3.txt).
- easylist.json and files in `scripts` directory is [BSD](LICENSE-BSD.txt).
- blocklist files is [CC-BY-3.0](LICENSE-CC-BY-3.0.txt).
