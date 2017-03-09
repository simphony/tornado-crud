Tornado WebAPI CHANGELOG
========================

What's new in Tornado WebAPI 0.5.0
----------------------------------

Summary
~~~~~~~

- Javascript interface now returns high level results instead of Ajax responses. (#42)
- WebAPI Exceptions in validation routines are propagated as is, instead of being converted (#41)
- Added Resource.validate_identifier to validate the identifier. It must return the
  identifier (#40)
- Resource.validate() is now Resource.validate_representation(). It must return the
  representation, either unchanged or after modifications. (#39)
- Fix: missing files are now correctly released (#37, #38)

What's new in Tornado WebAPI 0.4.0
----------------------------------

Summary
~~~~~~~

- Automatic creation of JavaScript API to access the resources. (#33)

What's new in Tornado WebAPI 0.3.0
----------------------------------

Summary
~~~~~~~

- Added Exists exception (#27)
- Force the resource identifier to be a string, 
  allowing transparent return of a numerical id (#28)
- Added validation method to check the incoming representation (#29)

What's new in Tornado WebAPI 0.2.0
----------------------------------

Summary
~~~~~~~

- Support for multiple registries (#16)
- Deprecated exception BadRequest in favor of BadRepresentation (#21)

What's new in Tornado WebAPI 0.1.0
----------------------------------

Summary
~~~~~~~

- Initial porting from simphony-remote 

