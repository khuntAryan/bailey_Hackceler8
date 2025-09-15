import React from 'react';

export default function Hero() {
    return (
        <section className="relative bg-gradient-to-br from-pink-700 to-indigo-900 text-white py-28 px-6">
            <div className="max-w-lg space-y-6">
                <h1 className="text-5xl font-extrabold drop-shadow-lg tracking-tight leading-tight">
                    Elevate Your <span className="text-pink-400">Fitness</span> Journey
                </h1>
                <p className="text-lg font-light tracking-wide max-w-md drop-shadow-md">
                    Join PowerGym and get access to elite trainers, world-class equipment, and personalized plans.
                </p>
            </div>
        </section>
    );
}