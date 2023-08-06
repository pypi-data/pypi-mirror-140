Multilayered Perceptron By Pranav Sai:

    #Network 2=InputSize,3=HiddenSize, 1=OutputSize
    
    net=Network(2,3,1)

    #Traning Data : training_inputs= hours slept,hours studied ; training_outputs= Grade of Test
    training_inputs = np.array(([2, 9], [1, 5], [3, 6]), dtype=float)

    training_outputs = np.array(([92], [86], [89]), dtype=float)

    net.train(training_inputs,training_outputs,1000)

    print("Predicted Output: " + str(net.run([2,3])))
