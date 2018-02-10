import React, { Component, PropTypes } from 'react';
import { Table, message, Popconfirm } from 'antd';
import * as jobitem from '../services/item';

class ItemList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            columns: [],
            loading: true,
        };
        if (props.selectedKey) {
            this.initStatus(props.selectedKey)
        }
    }

    componentWillReceiveProps(nextProp) {
        console.log(nextProp)
        this.initStatus(nextProp.selectedKey)
    }

    initStatus(key) {
        var self = this;
        console.log('initStatus')
        jobitem.queryItem({jobname: key, 'num': 500}).then(function(res) {
            var col = []
            var d = []
            if (res.data) {
              var cold = {}
              res.data.columns.map((c) => {
                  cold[c] = 1
              })
              res.data.columns.map((c) => {
                  if (!c.endsWith('url')) {
                      var curl = c + '_url'
                      if (c == 'title' || c == 'name' || c == 'repo') {
                          curl = 'url'
                      }
                      var cd = {title: c, dataIndex: c}
                      if (curl in cold) {
                          cd['render'] = (text, record) => <a href={record[curl]} target='_blank'>{text}</a>
                      }
                      col.push(cd)
                  }
              })
              d = res.data.data
            }
            self.setState({
                data: d,
                columns: col,
                loading: false,
            })
        })
    }

    render() {
        var {data, columns, loading} = this.state;
        // console.log('col: ' + columns)
        // console.log('data: ' + data)

        return (
          <Table dataSource={data} columns={columns}/>
        )
    }
}

export default ItemList;
