'use strict';

module.exports = {

    'GET /api': function (req, res) {
        setTimeout(function () {
            res.json({
                items: {
                    githubtrending: {
                        url: "http://localhost:5000/api/items?jobname=githubtrending"
                    },
                    xxxxxgithubtrending: {
                        url: "http://localhost:5000/api/items?jobname=githubtrending"
                    },
                    yyyyyygithubtrending: {
                        url: "http://localhost:5000/api/items?jobname=githubtrending"
                    },
                },
                yaml_config: "http://localhost:5000/api/_yaml"
            });
        }, 500);
    },

    'GET /api/items': function (req, res) {
        setTimeout(function () {
            res.json({
                columns: ['_crawl_time', 'desc', 'fork', 'id', 'lang', 'repo', 'star', 'today', 'url'],
                data: [{
                    __tablename__: "githubtrending",
                    _crawl_time: "Fri, 09 Feb 2018 16:00:31 GMT",
                    desc: "Be smart and embrace the future, today. The fastest web framework for Go in the Universe.",
                    fork: "",
                    id: 216,
                    lang: "",
                    repo: "kataras / iris",
                    star: "",
                    today: "",
                    url: "https://github.com/kataras/iris"
                }, {
                    __tablename__: "githubtrending",
                    _crawl_time: "Fri, 09 Feb 2018 15:00:15 GMT",
                    desc: "Normalize browsers' default style",
                    fork: "",
                    id: 215,
                    lang: "",
                    repo: "sindresorhus / modern-normalize",
                    star: "",
                    today: "",
                    url: "https://github.com/sindresorhus/modern-normalize"
                }]
            });
        }, 500);
    },
};
