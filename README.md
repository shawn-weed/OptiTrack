# OptiTrack
Open Source Asset Management

A more simpllified version is currently in use as a proof of concept. This is an open source version with in process feature improvements. *This code is not complete*. The README will be updated when this version of the software is functional.

OptiTrack was originally created as a simple way to manage Chromebooks in a K-12 environment. I am currently moving toward a more general asset management system that is highly configurable. It allows for quick assignment of an asset and the ability to loan a device by attaching to a 'fact' object in case the original device is in need of repair or the user otherwise needs another device.

The current improvements in progress are 

- switching to an ORM instead of direct SQL queries through SQLalchemy
- Added a Tableview from ttkbootstrap for easy export of data for reports, etc.
- Setting up multiple connection types and ability to use different database software
- Cleaning up and optimizing flow through the app for a better user experience
