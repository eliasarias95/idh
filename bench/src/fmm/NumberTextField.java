/****************************************************************************
Copyright (c) 2008, Colorado School of Mines and others. All rights reserved.
This program and accompanying materials are made available under the terms of
the Common Public License - v1.0, which accompanies this distribution, and is
available at http://www.eclipse.org/legal/cpl-v10.html
****************************************************************************/
package fmm;

import java.awt.*;
import java.text.*;
import javax.swing.*;
import javax.swing.text.*;

/**
 * A text field for numbers, either integer or floating-point values.
 * A number text field permits only numeric entries. Values may also be 
 * constrained by lower and upper bounds and to be integers.
 * <p>
 * The number displayed in a number text field is always a number or a
 * part of a number not yet completed. A number text field does not 
 * permit characters to be entered that could not be part of a number. 
 * <p>
 * When lower and upper bounds are specified, a number text field with 
 * keyboard focus will attempt to retain that focus until the displayed
 * value entered via the keyboard is within bounds.
 * <p>
 * Likewise, when constrained to be an integer, a number text field will
 * attempt to retain keyboard focus until the displayed value is an integer.
 * @author Dave Hale, Colorado School of Mines
 * @version 2008.06.21
 */
public class NumberTextField extends JFormattedTextField {
  private static final long serialVersionUID = 1L;

  /**
   * Constructs a number text field with no bounds.
   */
  public NumberTextField() {
    this(-Double.MAX_VALUE,Double.MAX_VALUE);
  }

  /**
   * Constructs a number text field with specified bounds on values.
   * @param vmin the minimum value.
   * @param vmax the maximum value.
   */
  public NumberTextField(double vmin, double vmax) {
    this(vmin,vmax,false);
  }

  /**
   * Constructs a number text field with specified constraints.
   * @param vmin the minimum value.
   * @param vmax the maximum value.
   * @param vint true, for values constrained to integers; false, otherwise.
   */
  public NumberTextField(double vmin, double vmax, final boolean vint) {
    super(new CustomFormatter() {
      protected DocumentFilter getDocumentFilter() {
        return _filter;
      }
      private CustomFilter _filter = new CustomFilter(vint);
    });
    _vmin = vmin;
    _vmax = vmax;
    _vint = vint;
    setInputVerifier(new InputVerifier() {
      public boolean verify(JComponent component) {
        String s = getText();
        double v;
        try {
          v = (_vint)?Integer.parseInt(s):Double.parseDouble(s);
        } catch (NumberFormatException e) {
          return false;
        }
        return _vmin<=v && v<=_vmax;
      }
    });
  }

  /**
   * Sets the min-max range of values.
   * @param vmin the minimum value.
   * @param vmax the maximum value.
   */
  public void setValueRange(double vmin, double vmax) {
    _vmin = vmin;
    _vmax = vmax;
  }

  /**
   * Sets the value of this number text field.
   * @param object the value object; must be a Number.
   */
  public void setValue(Object object) {
    Number n = (Number)object;
    double v = n.doubleValue();
    if (v<_vmin) v = _vmin;
    if (v>_vmax) v = _vmax;
    if (_vint)
      v = (int)v;
    super.setValue(v);
  }

  /**
   * Sets the value of this number text field as a double.
   * @param v the value.
   */
  public void setDouble(double v) {
    setValue(new Double(v));
  }

  /**
   * Sets the value of this number text field as a float.
   * @param v the value.
   */
  public void setFloat(float v) {
    setDouble(v);
  }

  /**
   * Sets the value of this number text field as an int.
   * @param v the value.
   */
  public void setInt(int v) {
    setDouble(v);
  }

  /**
   * Gets the value of this number text field as a double.
   * @return the value.
   */
  public double getDouble() {
    Number value = (Number)super.getValue();
    return value.doubleValue();
  }

  /**
   * Gets the value of this number text field as a float.
   * @return the value.
   */
  public float getFloat() {
    return (float)getDouble();
  }

  /**
   * Gets the value of this number text field as an int.
   * @return the value.
   */
  public int getInt() {
    return (int)getDouble();
  }

  ///////////////////////////////////////////////////////////////////////////
  // private

  private double _vmin = -Double.MAX_VALUE; // min value
  private double _vmax = Double.MAX_VALUE; // max value
  private boolean _vint = false; // true for only integer values

  // Formatter that uses a specified printf-style format for display.
  // Also removes any insignificant trailing zeros or decimal point.
  private static class CustomFormatter extends DefaultFormatter {
    public CustomFormatter() {
      this("%1.6g");
    }
    public CustomFormatter(String format) {
      _format = format;
      setOverwriteMode(true);
      setAllowsInvalid(false);
    }
    public String valueToString(Object v) throws ParseException {
      if (!(v instanceof Double)) 
        throw new ParseException("value is not a double",0);
      String s = String.format(_format,(Double)v);
      int len = s.length();
      int iend = s.indexOf('e');
      if (iend<0)
        iend = s.indexOf('E');
      if (iend<0)
        iend = len;
      int ibeg = iend;
      if (s.indexOf('.')>0) {
        while (ibeg>0 && s.charAt(ibeg-1)=='0')
          --ibeg;
        if (ibeg>0 && s.charAt(ibeg-1)=='.')
          --ibeg;
      }
      if (ibeg<iend) {
        String sb = s.substring(0,ibeg);
        s = (iend<len)?sb+s.substring(iend,len):sb;
      }
      return s;
    }
    public Object stringToValue(String s) throws ParseException {
      Double v = null;
      try {
        v = Double.parseDouble(s);
      } catch (NumberFormatException e) {
        throw new ParseException("cannot convert string to double",0);
      }
      return v;
    }
    private String _format;
  }

  // Ensures that the text in the field is always a valid part of a 
  // number. The trick here is to append a zero to the changed text.
  // (The changed text is the current text with the proposed change.)
  // If the changed text with zero appended is a valid number, then 
  // we permit the proposed change. Otherwise, we beep.
  private static class CustomFilter extends DocumentFilter {
    public CustomFilter(boolean vint) {
      _vint = vint;
    }
    public void insertString(
      FilterBypass fb, int off, String string, AttributeSet as)
      throws BadLocationException
    {
      String sc = getCurrentText(fb);
      StringBuilder sb = new StringBuilder(sc);
      String sn = sb.insert(off,string).toString();
      if (isPartOfNumber(sn)) {
        super.insertString(fb,off,string,as);
      } else {
        Toolkit.getDefaultToolkit().beep();
      }
    }
    public void replace(
      FilterBypass fb, int off, int len, String string, AttributeSet as)
      throws BadLocationException
    {
      String sc = getCurrentText(fb);
      StringBuilder sb = new StringBuilder(sc);
      String sn = sb.replace(off,off+len,string).toString();
      if (isPartOfNumber(sn)) {
        super.replace(fb,off,len,string,as);
      } else {
        Toolkit.getDefaultToolkit().beep();
      }
    }
    private boolean _vint;
    private String getCurrentText(FilterBypass fb) {
      Document d = fb.getDocument();
      String s = null;
      try {
        s = d.getText(0,d.getLength());
      } catch (BadLocationException e) {
        assert false:"exception not possible: "+e;
      }
      return s;
    }
    private boolean isPartOfNumber(String s) {
      s = s+"0";
      try {
        if (_vint) {
          int i = Integer.parseInt(s);
        } else {
          double d = Double.parseDouble(s);
        }
        return true;
      } catch (NumberFormatException e) {
        return false;
      }
    }
  }
}