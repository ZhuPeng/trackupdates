import React from 'react';
import ReactDOM from 'react-dom';
import './IndexLayout.css';
import * as jobitem from '../services/item';
import ItemList from './ItemList';
import { Layout, Menu, Icon, Select } from 'antd';
const { Header, Sider, Content } = Layout;
const Option = Select.Option;

class IndexLayout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            collapsed: false, 
            data: '',
            loading: true,
            selectedKey: '',
            formatStyle: 'html',
        };
        this.initStatus()
    }

    initStatus() {
        var self = this;
        jobitem.queryApiIndex().then(function(res) {
            var selectedKey = '';
            for (var i in res.data.items) {
                selectedKey = i
                break
            }
            console.log(res.data)
            self.setState({
                data: res.data,
                selectedKey: selectedKey,
                loading: false,
            })
        })
    }

    toggle = () => {
        console.log(this.props)
        this.setState({
            collapsed: !this.state.collapsed,
        });
    }

    handleClick = (e) => {
        console.log('click: ', e.key);
        this.setState({
            selectedKey: e.key,
        });
    }

    handleChange(value) {
        console.log(`selected ${value}`);
        this.setState({formatStyle: value})
    }

    render() {
        var {collapsed, data, loading, selectedKey, formatStyle} = this.state;
        var menuItem = []
        if (!loading) {
            for (var i in data.items) {
                menuItem.push(<Menu.Item key={i}><span>{i}</span></Menu.Item>)
            }
        }

        return (
          <Layout>
            <Sider trigger={null} collapsible collapsed={collapsed} >
              <div className="logo"></div>
              <Menu theme="dark" mode="inline" onClick={this.handleClick} selectedKeys={[selectedKey]}>
                {menuItem}
              </Menu>
            </Sider>
            <Layout>
              <Header style={{ background: '#fff', padding: 0 }}>
                <Icon className="trigger" type={collapsed ? 'menu-unfold' : 'menu-fold'} onClick={this.toggle} />
                <Select defaultValue={formatStyle} style={{ width: 120 }} onChange={this.handleChange.bind(this)}>
                  <Option value="html">HTML</Option>
                  <Option value="markdown">Markdown</Option>
                  <Option value="json">Table</Option>
                </Select>
              </Header>
              <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
                <ItemList selectedKey={selectedKey} formatStyle={formatStyle}/>
              </Content>
            </Layout>
          </Layout>
      );
    }
}

export default IndexLayout;
