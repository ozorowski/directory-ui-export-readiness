from article import helpers


def test_build_twitter_link(rf):
    request = rf.get('/')
    actual = helpers.build_twitter_link(
        request=request,
        markdown_file_path='article/markdown/01_do-research-first.md',
    )

    assert actual == (
        'https://twitter.com/intent/tweet'
        '?text=Export Readiness - Do research first http://testserver/'
    )


def test_build_facebook_link(rf):
    request = rf.get('/')
    actual = helpers.build_facebook_link(
        request=request,
        markdown_file_path='article/markdown/01_do-research-first.md',
    )
    assert actual == (
        'http://www.facebook.com/share.php?u=http://testserver/'
    )


def test_build_linkedin_link(rf):
    request = rf.get('/')
    actual = helpers.build_linkedin_link(
        request=request,
        markdown_file_path='article/markdown/01_do-research-first.md',
    )

    assert actual == (
        'https://www.linkedin.com/shareArticle?mini=true&'
        'url=http://testserver/&'
        'title=Export Readiness - Do research first&source=LinkedIn'
    )


def test_build_email_link(rf):
    request = rf.get('/')
    actual = helpers.build_email_link(
        request=request,
        markdown_file_path='article/markdown/01_do-research-first.md',
    )

    assert actual == (
        'mailto:?body=Export Readiness - Do research first'
        '&subject=http://testserver/'
    )