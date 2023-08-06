/* FEAT
copyright 2017 William La Cava
license: GNU/GPL v3
*/
#ifndef NODE_SIN
#define NODE_SIN

#include "../n_Dx.h"

namespace FT{

    namespace Pop{
        namespace Op{
        	class NodeSin : public NodeDx
            {
            	public:
            	
            		NodeSin(vector<float> W0 = vector<float>());
            		
                    /// Evaluates the node and updates the state states. 
                    void evaluate(const Data& data, State& state);

                    /// Evaluates the node symbolically
                    void eval_eqn(State& state);

                    ArrayXf getDerivative(Trace& state, int loc);
                    
                protected:
                    NodeSin* clone_impl() const override;  
                    NodeSin* rnd_clone_impl() const override;  
            };
        }
    }
}	

#endif
