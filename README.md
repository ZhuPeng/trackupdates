# trackupdates
A simple yaml-based xpath crawler and esay tracking site updates.


## Getting Started
```
git clone git@github.com:ZhuPeng/trackupdates.git
cd trackupdates
pip install -r requirements.txt
# update the smtp mail configure to your own
python trackupdates/trackupdates.py examples/githubtrending.yaml --test
```
The above script running as the yaml configuration file specified, it will track the updates of [github trending](https://github.com/trending?since=daily) with certain `cron` time and notify the contents which match the keywords you specified.

## Yaml Configuration
The yaml configuration file syntax was inspired by [Prometheus](https://github.com/prometheus/prometheus) and [Alertmanager](https://github.com/prometheus/alertmanager). This is an example configuration that track the updates of github trending and getting notification when there was a new `Python` project. The crawl results store in `github.db` with `sqlite`.

```yaml
global:
  # The smarthost and SMTP sender used for mail notifications.
  smtp_smarthost: 'example.smtp.com:587'
  smtp_from: 'example@examle.com'
  smtp_auth_username: 'example@example.com'
  smtp_auth_password: 'example'

  store: 'github.db'

jobs:
- name: 'githubtrending'
  # run every one hour at 0 minute
  cron: '*/1|0'
  url:
    test_target: 'examples/githubtrending'
    target: 'https://github.com/trending{lang}?since=daily'
    query_parameter:
      lang: '/python,/go,'
  parser: 'githubtrending'
  update:
    receiver: 'example'
    match:
      lang: 'Python'

parsers:
- name: 'githubtrending'
  base_url: 'https://github.com'
  base_xpath:
  - "//li[@class='col-12 d-block width-full py-4 border-bottom']"
  attr:
    url: 'div/h3/a/@href'
    repo: 'div/h3/a'
    desc: "div[@class='py-1']/p"
    lang: "div/span[@itemprop='programmingLanguage']"
    star: "div/a[@aria-label='Stargazers']"
    fork: "div/a[@aria-label='Forks']"
    today: "div/span[@class='float-right']"
  format:
    markdown: '[{lang}: {repo}]({url}), star: {star}, fork: {fork}, today-star: {today} <br> {desc}'
    html: '<p><a href="{url}">{lang}: {repo}</a> start: {star}, fork: {fork}, today-star: {today}, {desc}</p>'

receivers:
- name: 'example'
  email_configs:
    to:
    - 'example@example.com'
```

## License
MIT, please see [LICENSE](LICENSE).
