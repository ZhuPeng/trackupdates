import React from 'react';
import { connect } from 'dva';
import styles from './IndexPage.css';
import IndexLayout from '../components/IndexLayout';

function IndexPage() {
  return (
    <IndexLayout name='haha'></IndexLayout>
  );
}

IndexPage.propTypes = {
};

export default connect()(IndexPage);
