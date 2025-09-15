import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

export default function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    return (
        <header className="bg-gradient-to-r from-indigo-900 via-purple-900 to-pink-900 text-white shadow-md sticky top-0 z-50">
            <div className="container mx-auto flex justify-between items-center p-5">
                <div className="text-3xl font-extrabold tracking-tight cursor-pointer select-none">
                    <NavLink to="/" className="hover:text-pink-400">PowerGym</NavLink>
                </div>
                {/* Navigation and mobile menu code */}
            </div>
        </header>
    );
}