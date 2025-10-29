import React from "react";
import { SpinnerCircular } from 'spinners-react';

interface LoadingOverlayProps {
    isOpen: boolean;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ isOpen }) => {
  // We want to only show this if it appears for more than the given time
  const MIN_LOAD_TIME = 250;

  const [show, setShow] = React.useState(false);

  React.useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        setShow(true);
      }, MIN_LOAD_TIME);
      return () => clearTimeout(timer);
    } else {
      setShow(false);
    }
  }, [isOpen]);

  return show ? (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-[10000]" data-testid="modal-overlay">
      <div className="bg-white p-6 rounded-lg shadow-lg w-48">
        <h2 className="text-center text-lg font-semibold mb-4">Loading...</h2>
        <div className="flex justify-center">
          <SpinnerCircular
            size={60}
            thickness={250}
            color="rgb(59,130,246)"
            secondaryColor="rgba(0,0,0,0.1)"
          />
        </div>
      </div>
    </div>
  ) : null;
};

export default LoadingOverlay;
