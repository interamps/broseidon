---

name: webbuild
description: Build and audit production-ready websites. Use when creating, reviewing, or deploying websites, especially Vite/React apps, to catch SEO, accessibility, UX, performance, security, legal, and production-readiness issues.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Web Build Rules

Build websites that are production-ready, accessible, performant, secure, indexable, and credible. Avoid generic AI/vibe-coded design patterns.

## SEO & Discoverability

* Give every page a unique `<title>`.
* Add a unique, useful meta description per page.
* Add a canonical URL.
* Add Open Graph metadata and a social-share image.
* Add appropriate structured data/schema; use LocalBusiness schema for local businesses.
* Add `robots.txt` and `sitemap.xml`.
* Add `llms.txt` where appropriate.
* Do not block search/AI crawlers unless explicitly required.
* Set the correct `<html lang>`.
* Use exactly one meaningful H1 per page.
* Use semantic heading hierarchy.
* Add internal links.
* Add breadcrumbs where useful.
* Create a custom 404 page.
* Ensure production pages render meaningful HTML; do not ship an empty source shell where server/prerendered content is expected.
* Remove unnecessary source maps from production if they expose sensitive implementation details.

## Content & Credibility

* Use specific, factual copy instead of generic buzzwords.
* Remove unsupported claims.
* Use real reviews; never fabricate testimonials.
* Include real business/contact details.
* Add case studies where relevant.
* Provide at least 5 useful FAQs where appropriate.
* Include a clear response-time promise when offering support/services.
* Add a team photo when relevant.
* Include a thank-you page after successful forms/conversions.
* Use clear button labels.
* Ensure copyright/licensing is valid for all images and third-party assets.
* Avoid excessive em dashes and generic AI-style phrasing.

## Conversion & UX

* Put the primary CTA above the fold.
* Add a sticky mobile CTA where appropriate.
* Make important actions obvious.
* Provide loading, empty, success, and error states.
* Handle failed requests and API timeouts gracefully.
* Prevent duplicate submissions and payments.
* Ensure mobile breakpoints work correctly.
* Keep spacing and component behavior consistent.
* Make forms keyboard-friendly.
* Show useful validation and form error states.
* Check third-party embeds for usability, privacy, performance, and failure behavior.

## Accessibility

* Add meaningful `alt` text to every informative image; use empty alt text for purely decorative images.
* Check WCAG colour contrast.
* Ensure keyboard navigation works throughout the site.
* Use semantic HTML and correct heading hierarchy.
* Ensure controls have accessible names.
* Do not rely on colour alone to communicate state.
* Ensure focus states remain visible.
* Test forms and interactive components without a mouse.
* Fix accessibility errors before deployment.

## Design Quality

Avoid generic AI/vibe-coded visual patterns unless they are deliberately part of the design:

* Purple-to-blue gradients
* Gradient hero text
* Emojis in headings
* Inter everywhere
* Space Grotesk + Instrument Serif as a default pairing
* Serif italic accent text
* Coloured-border card grids
* Glassmorphism cards
* Grain over gradients
* Three icon boxes in a row
* Badge-above-headline layouts used without purpose
* Lucide icons everywhere
* Untouched shadcn UI
* Generic fade-in-on-scroll animations
* Cursor-following beams/effects
* Buttons that merely fade on hover

Use intentional typography, spacing, hierarchy, imagery, motion, and component design instead of decoration for its own sake.

## Performance

* Keep JS bundles small; remove unnecessary dependencies and code.
* Compress and appropriately size images.
* Lazy-load non-critical resources.
* Cache repeat requests where appropriate.
* Optimise DB queries.
* Add DB indexes for common query patterns.
* Paginate large result sets.
* Limit upload sizes.
* Monitor uptime.
* Add error logging.
* Test under simultaneous users/concurrent requests.
* Remove unnecessary client-side code.
* Avoid shipping development/debug tooling in production.
* Check browser console for errors and warnings before release.

## Backend & API Reliability

* Validate all user input server-side.
* Enforce API rate limits.
* Set API/resource limits.
* Set spending caps for paid APIs/services.
* Handle API failures and timeouts.
* Return safe, useful errors without exposing internals.
* Prevent duplicate operations, subscriptions, and payments.
* Enforce authorization server-side.
* Test backup restoration.
* Verify external dependencies and third-party services fail safely.

## Security

Check for:

* XSS
* CSRF
* SQL injection
* NoSQL injection
* SSRF
* Path traversal
* Insecure file uploads
* Broken password-reset flows
* Weak session management
* Weak or exposed JWT secrets
* Permissive CORS
* Missing rate limits
* Exposed environments
* Default credentials
* Unsigned webhooks
* Client-side-only payment/security checks
* IDOR/BOLA
* APIs trusting unvalidated user input
* Exposed logs
* Exposed source maps containing sensitive information
* Exposed DB credentials
* Public `.env` files
* Hardcoded API keys/secrets
* Secrets committed to Git or Git history
* Missing authentication
* Missing server-side authorization
* Cross-user data access
* Overly permissive DB/storage permissions
* Misconfigured Firebase, Supabase, S3, or other storage
* Unprotected admin routes
* Debug pages/dev tools exposed in production
* Build logs leaking secrets
* Verbose errors/stack traces exposing internals

Never put secrets in frontend JavaScript. Treat all client-side code and data as public.

## Privacy, Legal & Consent

Where applicable, provide:

* Privacy Policy

* Terms & Conditions

* Refund Policy

* Cookie Policy

* Cookie consent

* Form/data-collection consent

* Real business/contact details

* Only necessary data collection

* Appropriate tracking disclosures

* Install analytics only when appropriate and disclose tracking.

* Check cookie consent before non-essential tracking.

* Check local legal requirements for the target jurisdiction.

* Review third-party embeds, analytics, payment providers, and other processors for privacy implications.

* Do not collect data merely because it is technically available.

## Production Checklist

Before deployment, verify:

* Custom 404
* Unique page titles/descriptions
* Canonical URLs
* CTA above fold
* Internal links/breadcrumbs
* Favicon set
* `robots.txt`
* `sitemap.xml`
* Open Graph/social image
* Structured data
* `llms.txt` where appropriate
* Correct `lang`
* One H1/page
* Alt text
* Mobile layout/breakpoints
* Sticky mobile CTA where appropriate
* Loading/error/empty states
* Thank-you flow
* Privacy/Terms/Refund/Cookie pages as applicable
* Cookie consent
* Analytics/tracking configuration
* Real business details
* Compressed assets
* Accessibility/contrast/keyboard checks
* Console errors resolved
* API limits/rate limits
* Security checks completed
* Error logging
* Uptime monitoring
* Backup restoration tested
* Concurrent-user testing
* Production secrets protected
* Third-party integrations tested
