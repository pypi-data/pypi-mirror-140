# Changelog

## 1.1.0

Instagram-friendly video output using AAC as output audio codec + usage improvements

- change output video ffmpeg arguments to support instagram uploads

- spotDL args split seperately from `invocate()`, allows for queries with spaces
  `e.g. pymtheg "sicko mode skrillex remix"`

- rewrote clip timestamp input loop

  Old:

  ```text
  pymtheg: info: enter the timestamp of clip start ([hh:mm:]ss)
    Travis Scott, Skrillex - SICKO MODE - Skrillex Remix: 0
  ```

  New:

  ```text
  pymtheg: info: enter timestamps in format [hh:mm:]ss
                 end timestamp can be relative, prefix with '+'
                 press enter to use given defaults
    Travis Scott, Skrillex - SICKO MODE - Skrillex Remix
      clip start: 0
        clip end: +15
  ```

## 1.0.1

Packaging fixes

## 1.0.0

Initial working release
