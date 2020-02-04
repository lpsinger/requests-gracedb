Changelog
=========

0.1.1 (2020-02-04)
------------------

-   Remove unused ``ligo`` namespace package.

0.1.0 (2020-02-03)
------------------

-   Fix a unit test failure in test_cert_reload due to a test X.509 certificate
    having an expiration date that was in the past. The workaround was to set
    the certificate's "not valid before" date to the distant past (2008-01-01)
    and its "not valid after" date to the distant future (3020-01-01). Maybe
    our great-great-grandchildren will be wiser.

-   Address all feedback from Pierre Chanial's code review:
    https://git.ligo.org/emfollow/requests-gracedb/issues/3

-   Rename package from ligo-requests to requests-gracedb to remove
    institution-specific branding.

0.0.1 (2019-12-12)
------------------

-   Initial release.
