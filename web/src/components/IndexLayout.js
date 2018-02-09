import React from 'react';
import ReactDOM from 'react-dom';
import './IndexLayout.css';
import * as jobitem from '../services/item';
import ItemList from './ItemList';
import { Layout, Menu, Icon } from 'antd';
const { Header, Sider, Content } = Layout;

class IndexLayout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            collapsed: false, 
            data: '',
            loading: true,
            selectedKey: '',
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
        console.log('click ', e);
        this.setState({
            selectedKey: e.key,
        });
    }

    render() {
        var {collapsed, data, loading, selectedKey} = this.state;
        var menuItem = []
        if (!loading) {
            for (var i in data.items) {
                menuItem.push(<Menu.Item key={i}><span>{i}</span></Menu.Item>)
            }
        } else {
            menuItem.push(<Menu.Item key="loading"><span>loading</span></Menu.Item>)
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
              </Header>
              <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
                {selectedKey && <ItemList selectedKey={selectedKey}/>}
              </Content>
            </Layout>
          </Layout>
      );
    }
}

export default IndexLayout;
