# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 0.2.0 - 2022-02-28
### Added
- ``duration`` field on Podcast which is retrieved in the admin on client side
  from the ``sound_url`` value
- Player component with a dynamic playlist using django-unicorn

### Changed
- Replace the server side validation of ``sound_url`` - controlled with the
  setting ``WEBRADIO_VALIDATE_PODCAST_URL`` - by a client side validation to
  ensure it is an audio file

## 0.1.0 - 2022-02-14

This is the initial release which provides the basis - e.g. the models, admin
views and chooser blocks.
