import { configureStore } from '@reduxjs/toolkit';

// For now, create a basic store. In a full implementation, you would add slices here
export const store = configureStore({
  reducer: {
    // Add your reducers here when needed
    // Example: auth: authSlice.reducer,
    // Example: routes: routesSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
