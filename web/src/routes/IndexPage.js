import React from 'react';
import { connect } from 'dva';
import IndexLayout from '../components/IndexLayout';

function IndexPage() {
  return (
    <IndexLayout />
  );
}

IndexPage.propTypes = {
};

export default connect()(IndexPage);
