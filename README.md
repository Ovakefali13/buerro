# buerro 🌯

This is a super cool PDA from super cool people.

Best deployed using the [Docker buerro *wrap*per](https://github.com/mariushegele/buerro_docker).

## Install

```
make install
```

## Test

```
make test
```

We are only unit testing the backend. The frontend is minimal and depends on browser functionality like geo location, push notifications, text-to-speech, speech-to-text etc. This would require E2E-tests.

## Deploy

```
make frontend &
make backend
```
