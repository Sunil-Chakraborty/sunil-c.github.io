README.txt

without use of media_hierarchy.txt
https://sunil-chakraborty.github.io/sunil-c.github.io/76_Batch_DVAS/dist/
https://tinyurl.com/Echoes-of-76-Batch

Use media_hierarchy.txt
https://sunil-chakraborty.github.io/sunil-c.github.io/76_Batch_DVAS/dist1/

Harinavi School / 76 Batch Gallery Builder Navigation and Media
Hierarchy Configuration

PURPOSE

Use media_hierarchy.txt as the single source of truth for navigation
configuration and media subgroups. Keep navigation names, subgroup
names, and external-link definitions in that text file rather than
maintaining separate copies in Python, HTML, and JavaScript.

The Python builder should read and parse the text file, validate its
contents, and pass the resulting configuration to the HTML template as
JSON. The template should render the supplied configuration. JavaScript
should handle interactions (such as opening and closing subgroup lists),
not define the navigation structure again.

RECOMMENDED RESPONSIBILITIES

1.  media_hierarchy.txt
    -   Defines navigation items and their display labels.
    -   Defines subgroup names for Photos, Videos, and Documents.
    -   Defines external-link labels and URLs.
    -   Records any ordering that should be visible in the navigation.
    -   Is the editable configuration source for these items.
2.  build_more.py
    -   Reads media_hierarchy.txt.
    -   Parses the configuration in one place.
    -   Validates section names, required fields, and external URLs.
    -   Matches media files to the configured groups/subgroups.
    -   Converts the parsed configuration to JSON for template
        insertion.
    -   Reports useful errors for malformed or missing configuration.
    -   Does not duplicate the subgroup list or navigation labels as
        separate hardcoded Python lists when they can be read from the
        text file.
3.  template.html
    -   Contains the layout and styling for the navigation and gallery.
    -   Receives the generated configuration from build_more.py.
    -   Does not contain a second manually maintained copy of the
        hierarchy.
    -   Keeps markup changes small and preserves existing gallery
        behaviour.
4.  JavaScript in template.html
    -   Builds or updates navigation/subgroup elements from the supplied
        data.
    -   Handles clicks, accordion behaviour, and opening external links.
    -   Does not hardcode subgroup names or repeat the hierarchy
        configuration.
    -   Keeps the existing rule that only Photos, Videos, and Documents
        take part in the subgroup accordion, unless the configuration is
        deliberately changed later.

SUGGESTED CONFIGURATION APPROACH

Extend the existing media_hierarchy.txt format rather than creating a
second configuration file. Keep the format simple and human-editable.

The file should be able to represent: - Main navigation item and display
order. - Subgroups belonging to Photos, Videos, and Documents. - Audio
Files as a main navigation item, without subgroups unless requested. -
External Links as a main navigation item with one or more label/URL
pairs. - Optional items that should be hidden when they have no entries.

Use one clearly documented syntax consistently. For example, a
section-based format could have sections for NAVIGATION, PHOTOS, VIDEOS,
DOCUMENTS, AUDIO, and EXTERNAL_LINKS. The exact syntax should be agreed
upon before changing the parser; do not mix this example with an
existing format without checking compatibility first.

EXTERNAL LINKS

Store each external link’s display label and full URL in the
configuration file. The builder should validate that each URL is a valid
HTTP or HTTPS URL and safely serialize the link data as JSON. The
template should render the links from that data rather than keeping a
separate hardcoded list.

If there are no external links, the External Links navigation item
should be hidden or disabled according to the chosen project behaviour.
Do not display empty or broken link entries.

PARSER AND TEMPLATE GUIDELINES

-   Parse the configuration once in Python.
-   Keep parsing and validation logic in small, named functions.
-   Escape or serialize data safely; do not build JavaScript JSON by
    manually joining strings.
-   Use the standard JSON serializer for data passed to the template.
-   Handle blank lines and comments consistently.
-   Show a clear error message for unknown sections or malformed
    entries.
-   Preserve the existing file naming, media ordering, captions,
    previews, and subgroup accordion behaviour unless a change is
    explicitly requested.
-   Avoid unrelated refactoring while introducing this design.

CHANGE WORKFLOW

1.  Back up the current working versions of build_more.py,
    template.html, and media_hierarchy.txt.
2.  Confirm the existing media_hierarchy.txt syntax and document it.
3.  Add only the missing navigation/link configuration to that file.
4.  Update build_more.py to parse the configuration and pass it to the
    template as JSON.
5.  Make the smallest necessary template/JavaScript changes to render
    it.
6.  Run a Python syntax check: python -m py_compile build_more.py
7.  Run the builder from the project directory: python build_more.py
8.  Check the generated dist/index.html and test:
    -   Main navigation order and labels.
    -   All configured media subgroups.
    -   Opening one subgroup accordion closes the other relevant
        subgroup lists.
    -   Audio Files behaviour remains unchanged.
    -   External Links displays every configured link and opens the
        correct URL.
    -   Empty optional sections are handled correctly.
    -   Existing photos, videos, documents, captions, and previews still
        work.
9.  Review the changes and confirm that unrelated files and behaviour
    were not altered before publishing to GitHub Pages.

IMPORTANT

This README describes the recommended design. It does not, by itself,
change the current parser or template. Before implementing a new format,
inspect the actual current media_hierarchy.txt and adapt the parser to
that format so existing hierarchy data is not lost or silently
reinterpreted.

CORE PRINCIPLE

One source of truth for navigation configuration; one parser in Python;
minimal template changes; no duplicated hierarchy definitions across
Python, HTML, and JavaScript.
