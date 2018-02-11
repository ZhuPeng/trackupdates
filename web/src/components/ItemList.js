import React from 'react';
import { Table, List } from 'antd';
import * as jobitem from '../services/item';

class ItemList extends React.Component {
    constructor(props) {
        super(props);
        var fmt = props.formatStyle || 'html'
        this.state = {
            data: [],
            columns: [],
            formatStyle: fmt,
            actualFormat: fmt,
        };
        if (props.selectedKey) {
            this.initStatus(props.selectedKey, fmt)
        }
    }

    componentWillReceiveProps(nextProp) {
        console.log(nextProp)
        var fmt = nextProp.formatStyle || this.state.formatStyle
        this.setState({
            formatStyle: fmt,
        })
        this.initStatus(nextProp.selectedKey, fmt)
    }

    initStatus(key, fmt) {
        var self = this;
        console.log('initStatus')
        jobitem.queryItem({jobname: key, 'num': 500, 'format': fmt}).then(function(res) {
            var col = []
            var d = []
            if (res.data) {
              console.log(res.data)
              var cold = {}
              res.data.columns.map((c) => {
                  cold[c] = 1
                  return ''
              })
              res.data.columns.map((c) => {
                  if (!c.endsWith('url')) {
                      var curl = c + '_url'
                      if (c === 'title' || c === 'name' || c === 'repo') {
                          curl = 'url'
                      }
                      var cd = {title: c, dataIndex: c}
                      if (curl in cold) {
                          cd['render'] = (text, record) => <a href={record[curl]} target='_blank'>{text}</a>
                      }
                      col.push(cd)
                  }
                  return ''
              })
              d = res.data.data
            }
            self.setState({
                data: d,
                columns: col,
                actualFormat: res.data.format,
            })
        })
    }

    render() {
        var {data, columns, actualFormat} = this.state;

        return (
          <div>
            {actualFormat === 'json' && <Table dataSource={data} columns={columns}/>}
            {(actualFormat === 'markdown' || actualFormat === 'html') && <List itemLayout="horizontal" dataSource={data} renderItem={item => (<List.Item><div dangerouslySetInnerHTML={{__html: item}}></div></List.Item>)}/>}
          </div>
        )
    }
}

export default ItemList;
