import React, { Component, PropTypes } from 'react';
import { Table, message, Popconfirm } from 'antd';
import * as jobitem from '../services/item';

class ItemList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            key: props.selectedKey, 
            data: '',
            loading: true,
            selectedKey: '',
        };
        if (props.selectedKey) {
            this.initStatus()
        }
    }

    initStatus() {
        var self = this;
        jobitem.queryItem({jobname: this.state.key}).then(function(res) {
            self.setState({
                data: res.data,
                loading: false,
            })
        })
    }

    componentWillReceiveProps(nextProp) {
        this.setState({
            key: nextProp.selectedKey,
            loading: true,
        })
        this.initStatus()
    }

    render() {
        var {key, data} = this.state;
        console.log(data)
        var col = []
        if (data.columns) {
          data.columns.map((c) => {
              col.push({
                  title: c,
                  dataIndex: c,
              })
          })
        }

        return (
          <Table dataSource={data.data} columns={col} />
        )
    }

}
export default ItemList;
