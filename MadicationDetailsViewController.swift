//
//  MedicationDetailsViewController.swift
//  MeDS
//
//  Created by Tech on 23/02/2023.
//

import UIKit
import SwiftSocket

class MedicationDetailsViewController: UIViewController {
    
   //these are outlets of views which are showing on interface
    @IBOutlet weak var txtDetails: UITextView!
    @IBOutlet weak var txtDosage: UITextView!
    @IBOutlet weak var txtTime: UITextView!
    @IBOutlet weak var txtCycle: UITextView!
    @IBOutlet weak var txtPills: UITextView!
    @IBOutlet weak var viewDetails: UIView!
    @IBOutlet weak var viewDosage: UIView!
    @IBOutlet weak var viewTime: UIView!
    @IBOutlet weak var viewCycle: UIView!
    @IBOutlet weak var viewPills: UIView!
    @IBOutlet weak var lblType: UILabel!
  
    //declare variables
    var type = 0
    var name = ""
    let userDefaults = UserDefaults.standard
    var medication = MedicationModel() //this is model on medication i.e name , dosage , time etc properties
    
    
    //socket variable declaration
    let host = "10.186.112.1"
    let port = 5000
    var client: TCPClient?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        //inialization of socket with port number and host address
        client = TCPClient(address: host, port: Int32(port))
        
        //this line will show the name of medication selected by user
        self.lblType.text = name
        
        //rounds out statistics labels
        self.viewDetails.layer.cornerRadius = 8
        self.viewDosage.layer.cornerRadius = 8
        self.viewTime.layer.cornerRadius = 8
        self.viewCycle.layer.cornerRadius = 8
        self.viewPills.layer.cornerRadius = 8
        
        //this method will fetch the previously entered data by user from local database and show the respective data
        self.fetchMedicationData()
        
        // Do any additional setup after loading the view.
    }
    
    //this method will make the connection with the socket
    func connectToSocket(){
        let sendString = "iapp"
        let strrr = medication.pills
        let stringSend = String(strrr.prefix(3))
        print("Response: \(stringSend)")
        var stringNum = stringSend.count
        let strNum = String(stringNum)
        var lengthNum = strNum.count
        let finalNum = String(lengthNum)
   //     print("Response: \(numLength)")
        let num = String(repeating: " ", count: (4-lengthNum))
        let newStr:String = strNum + num
        
        guard let client = client else { return }
        switch client.connect(timeout: 10) {
        case .success:
          print("Connected to host \(client.address)")
          if let response = sendRequest(string:sendString, using: client) {
              print("Response: \(response)")
          }
          if let response = sendRequest(string:newStr, using: client) {
              print("Response: \(response)")
          }
          if let response = sendRequest(string:stringSend, using: client) {
            print("Response: \(response)")
          }
            
   //       if let res = client.read(1024*10) {
     //         print("go")
       //   }
            
       //   let resp = String(bytes: res, encoding: .utf8)
        //  print(resp)
        
//        print("word")
        case .failure(let error):
            print(String(describing: error))
        }
        
    }
    
    //this method will send the data to socket
    private func sendRequest(string: String, using client: TCPClient) -> String? {
      print("Sending data ... ")
      switch client.send(string: string) {
      case .success:
        return readResponse(from: client)
      case .failure(let error):
          print(String(describing: error))
        return nil
      }
    }
    
    //this method will read the response from socket
    private func readResponse(from client: TCPClient) -> String? {
      guard let response = client.read(4) else { return nil }
      return String(bytes: response, encoding: .utf8)
    }
    
    
    //this method will save the entered data to local database for the selected medication type
    //also you can call the connect to socket method here to send entered data to your socket
    @IBAction func actionSave(_ sender: Any) {
        do {
            self.saveMedication() // this method will set the data to model
            connectToSocket()
            try userDefaults.setObject(medication, forKey: "\(type)") //this method will save the model to local database
        } catch {
            print(error.localizedDescription)
        }
        self.navigationController?.popViewController(animated: true)
    }
    
        //this method will display data which is pulled from local database
    func setMedicationData(){
        self.txtPills.text = medication.pills
        self.txtCycle.text = medication.cycle
        self.txtTime.text = medication.time
        self.txtDosage.text = medication.dosage
        self.txtPills.text = medication.pills
    }
    
    // this method will set the data to model
    func saveMedication(){
        medication.pills = self.txtPills.text ?? ""
        medication.cycle =  self.txtCycle.text  ?? ""
         medication.time = self.txtTime.text ?? ""
         medication.dosage = self.txtDosage.text ?? ""
         medication.pills = self.txtPills.text ?? ""
    }
    
    //this method will fetch the data from database
    func fetchMedicationData(){
        do {
            medication = try userDefaults.getObject(forKey: "\(type)", castTo: MedicationModel.self)
            self.setMedicationData()
        } catch {
            print(error.localizedDescription)
        }
    }

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
