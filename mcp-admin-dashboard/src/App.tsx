import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Servers from './pages/Servers';
import Search from './pages/Search';
import Settings from './pages/Settings';

const App: React.FC = () => {
    return (
        <Router>
            <Layout>
                <Switch>
                    <Route path="/" exact component={Dashboard} />
                    <Route path="/documents" component={Documents} />
                    <Route path="/servers" component={Servers} />
                    <Route path="/search" component={Search} />
                    <Route path="/settings" component={Settings} />
                </Switch>
            </Layout>
        </Router>
    );
};

export default App;