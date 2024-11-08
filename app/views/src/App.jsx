import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// import Layout from './components/layout';
// import TaskList from './pages/taskList';
// import TaskEdit from './pages/taskEdit';
// import CategoryList from './pages/categoryList';
// import Login from './pages/login';
// import Register from './pages/register';

const queryClient = new QueryClient();

function App() {
    return (
        // <QueryClientProvider client={queryClient}>
        //     <Router>
        //         <Routes>
        //             <Route path='/login' element={<Login />} />
        //             <Route path='/register' element={<Register />} />
        //             <Route path='/' element={<Layout />}>
        //                 <Route index element={<TaskList />} />
        //                 <Route path='tasks/:id' element={<TaskEdit />} />
        //                 <Route path='categories' element={<CategoryList />} />
        //             </Route>
        //         </Routes>
        //     </Router>
        // </QueryClientProvider>
        <>
            <p>App</p>
        </>
    );
}

export default App;
